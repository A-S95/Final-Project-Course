import csv
import io
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dates import month_bounds
from app.core.exceptions import (
    InvalidReceiptError,
    InvalidTransactionError,
    ReceiptNotFoundError,
    SharedExpenseDuplicateError,
    TransactionNotFoundError,
)
from app.models.account import Account
from app.models.category import CategoryType
from app.models.transaction import Transaction, TransactionType
from app.repositories import household_repository, transaction_repository
from app.services import account_service, category_service

# Foto ao talão ou fatura digitalizada — os dois casos reais.
ALLOWED_RECEIPT_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_RECEIPT_SIZE_BYTES = 8 * 1024 * 1024  # chega para foto/PDF, evita encher o disco

_TYPE_LABELS = {
    TransactionType.INCOME: "Receita",
    TransactionType.EXPENSE: "Despesa",
    TransactionType.TRANSFER: "Transferência",
}


def _receipt_path(transaction_id: uuid.UUID) -> Path:
    directory = Path(settings.uploads_dir) / "receipts"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / str(transaction_id)


def _validate_combination(
    type: TransactionType,
    account_id: uuid.UUID,
    destination_account_id: uuid.UUID | None,
    category_id: uuid.UUID | None,
) -> None:
    if type == TransactionType.TRANSFER:
        if destination_account_id is None:
            raise InvalidTransactionError("Uma transferência exige uma conta de destino.")
        if destination_account_id == account_id:
            raise InvalidTransactionError(
                "A conta de destino tem de ser diferente da conta de origem."
            )
        if category_id is not None:
            raise InvalidTransactionError("Uma transferência não pode ter categoria.")
    else:
        if category_id is None:
            raise InvalidTransactionError("Escolhe uma categoria.")
        if destination_account_id is not None:
            raise InvalidTransactionError("Só uma transferência pode ter conta de destino.")


def _validate_category_type(type: TransactionType, category_type: CategoryType) -> None:
    if type.value != category_type.value:
        raise InvalidTransactionError(
            "O tipo da categoria tem de corresponder ao tipo da transação."
        )


def _check_shared_duplicate(
    db: Session,
    *,
    user_id: uuid.UUID,
    category_id: uuid.UUID,
    amount: Decimal,
    date: date,
    allow_duplicate: bool,
) -> None:
    """Uma despesa partilhada é um custo da casa, lançado uma só vez por quem pagou.
    Se outro membro do agregado já tem uma despesa partilhada igual (mesma categoria
    e valor) neste mês, recusa com 409 — provável lançamento em duplicado. O cliente
    reenvia com `allow_duplicate=True` (o casal confirmou que são mesmo duas)."""
    if allow_duplicate:
        return
    membership = household_repository.get_membership_for_user(db, user_id)
    if membership is None:
        return

    category = category_service.get_category(db, user_id=user_id, category_id=category_id)
    month_start, next_month_start = month_bounds(date)
    owner_name = transaction_repository.find_shared_expense_duplicate(
        db,
        member_user_ids=household_repository.member_user_ids(db, membership.household_id),
        exclude_user_id=user_id,
        category_name=category.name,
        amount=amount,
        month_start=month_start,
        next_month_start=next_month_start,
    )
    if owner_name is not None:
        first_name = owner_name.split(" ")[0]
        raise SharedExpenseDuplicateError(
            f"{first_name} já lançou uma despesa partilhada de {amount:.2f}€ em "
            f"«{category.name}» este mês. Uma despesa partilhada deve ser lançada só "
            f"uma vez pelo agregado — confirma se queres mesmo lançá-la à mesma."
        )


def _apply_balance_effect(
    type: TransactionType,
    account: Account,
    destination: Account | None,
    amount: Decimal,
    *,
    sign: int,
) -> None:
    if type == TransactionType.INCOME:
        account.current_balance += sign * amount
    elif type == TransactionType.EXPENSE:
        account.current_balance -= sign * amount
    else:  # TRANSFER
        account.current_balance -= sign * amount
        if destination is not None:
            destination.current_balance += sign * amount


def list_transactions(
    db: Session,
    *,
    user_id: uuid.UUID,
    account_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    type: TransactionType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[Transaction]:
    return transaction_repository.list_by_user(
        db,
        user_id,
        account_id=account_id,
        category_id=category_id,
        type=type,
        date_from=date_from,
        date_to=date_to,
    )


def export_transactions_csv(
    db: Session,
    *,
    user_id: uuid.UUID,
    account_id: uuid.UUID | None = None,
    category_id: uuid.UUID | None = None,
    type: TransactionType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> bytes:
    """CSV das transações, com os mesmos filtros da listagem. Separador `;` e
    vírgula decimal — o que o Excel em português espera ao abrir o ficheiro."""
    transactions = list_transactions(
        db,
        user_id=user_id,
        account_id=account_id,
        category_id=category_id,
        type=type,
        date_from=date_from,
        date_to=date_to,
    )
    account_names = {a.id: a.name for a in account_service.list_accounts(db, user_id=user_id)}
    category_names = {c.id: c.name for c in category_service.list_categories(db, user_id=user_id)}

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(
        ["Data", "Tipo", "Descrição", "Valor", "Conta", "Conta destino", "Categoria", "Partilhada"]
    )
    for t in transactions:
        writer.writerow(
            [
                t.date.isoformat(),
                _TYPE_LABELS[t.type],
                t.description or "",
                f"{t.amount:.2f}".replace(".", ","),
                account_names.get(t.account_id, ""),
                account_names.get(t.destination_account_id, "")
                if t.destination_account_id
                else "",
                category_names.get(t.category_id, "") if t.category_id else "",
                "Sim" if t.is_shared else "Não",
            ]
        )
    # BOM UTF-8: sem isto o Excel no Windows abre os acentos como "Ã§".
    return b"\xef\xbb\xbf" + buffer.getvalue().encode("utf-8")


def get_transaction(db: Session, *, user_id: uuid.UUID, transaction_id: uuid.UUID) -> Transaction:
    transaction = transaction_repository.get_by_id_for_user(db, transaction_id, user_id)
    if transaction is None:
        raise TransactionNotFoundError
    return transaction


def create_transaction(
    db: Session,
    *,
    user_id: uuid.UUID,
    account_id: uuid.UUID,
    destination_account_id: uuid.UUID | None,
    category_id: uuid.UUID | None,
    type: TransactionType,
    amount: Decimal,
    description: str | None,
    date: date,
    is_shared: bool = False,
    allow_duplicate: bool = False,
) -> Transaction:
    _validate_combination(type, account_id, destination_account_id, category_id)

    account = account_service.get_account(db, user_id=user_id, account_id=account_id)
    destination = None
    if destination_account_id is not None:
        destination = account_service.get_account(
            db, user_id=user_id, account_id=destination_account_id
        )
    if category_id is not None:
        category = category_service.get_category(db, user_id=user_id, category_id=category_id)
        _validate_category_type(type, category.type)

    if is_shared and type == TransactionType.EXPENSE and category_id is not None:
        _check_shared_duplicate(
            db,
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            date=date,
            allow_duplicate=allow_duplicate,
        )

    transaction = transaction_repository.create(
        db,
        user_id=user_id,
        account_id=account_id,
        destination_account_id=destination_account_id,
        category_id=category_id,
        type=type,
        amount=amount,
        description=description,
        date=date,
        is_shared=is_shared,
    )
    _apply_balance_effect(type, account, destination, amount, sign=1)
    db.flush()
    return transaction


def update_transaction(
    db: Session,
    *,
    user_id: uuid.UUID,
    transaction_id: uuid.UUID,
    account_id: uuid.UUID,
    destination_account_id: uuid.UUID | None,
    category_id: uuid.UUID | None,
    type: TransactionType,
    amount: Decimal,
    description: str | None,
    date: date,
    is_shared: bool = False,
    allow_duplicate: bool = False,
) -> Transaction:
    transaction = get_transaction(db, user_id=user_id, transaction_id=transaction_id)
    _validate_combination(type, account_id, destination_account_id, category_id)

    # Reverte o efeito da transação tal como estava antes de editar...
    old_account = account_service.get_account(
        db, user_id=user_id, account_id=transaction.account_id
    )
    old_destination = None
    if transaction.destination_account_id is not None:
        old_destination = account_service.get_account(
            db, user_id=user_id, account_id=transaction.destination_account_id
        )
    _apply_balance_effect(
        transaction.type, old_account, old_destination, transaction.amount, sign=-1
    )

    # ...e aplica o efeito da nova versão (contas podem ter mudado).
    new_account = account_service.get_account(db, user_id=user_id, account_id=account_id)
    new_destination = None
    if destination_account_id is not None:
        new_destination = account_service.get_account(
            db, user_id=user_id, account_id=destination_account_id
        )
    if category_id is not None:
        category = category_service.get_category(db, user_id=user_id, category_id=category_id)
        _validate_category_type(type, category.type)

    if is_shared and type == TransactionType.EXPENSE and category_id is not None:
        _check_shared_duplicate(
            db,
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            date=date,
            allow_duplicate=allow_duplicate,
        )

    _apply_balance_effect(type, new_account, new_destination, amount, sign=1)

    transaction.account_id = account_id
    transaction.destination_account_id = destination_account_id
    transaction.category_id = category_id
    transaction.type = type
    transaction.amount = amount
    transaction.description = description
    transaction.date = date
    transaction.is_shared = is_shared

    db.flush()
    return transaction


def delete_transaction(db: Session, *, user_id: uuid.UUID, transaction_id: uuid.UUID) -> None:
    transaction = get_transaction(db, user_id=user_id, transaction_id=transaction_id)

    account = account_service.get_account(db, user_id=user_id, account_id=transaction.account_id)
    destination = None
    if transaction.destination_account_id is not None:
        destination = account_service.get_account(
            db, user_id=user_id, account_id=transaction.destination_account_id
        )
    _apply_balance_effect(transaction.type, account, destination, transaction.amount, sign=-1)

    # Sem isto o ficheiro do recibo fica órfão em disco (sem FK a apontar para ele).
    if transaction.receipt_content_type is not None:
        _receipt_path(transaction.id).unlink(missing_ok=True)

    transaction_repository.delete(db, transaction)
    db.flush()


def save_receipt(
    db: Session,
    *,
    user_id: uuid.UUID,
    transaction_id: uuid.UUID,
    content: bytes,
    content_type: str,
) -> Transaction:
    transaction = get_transaction(db, user_id=user_id, transaction_id=transaction_id)

    if content_type not in ALLOWED_RECEIPT_CONTENT_TYPES:
        raise InvalidReceiptError(
            "Tipo de ficheiro não suportado. Usa uma imagem (JPEG, PNG, WEBP) ou um PDF."
        )
    if len(content) > MAX_RECEIPT_SIZE_BYTES:
        raise InvalidReceiptError("O ficheiro é demasiado grande (máximo 8MB).")

    _receipt_path(transaction.id).write_bytes(content)
    transaction.receipt_content_type = content_type
    db.flush()
    return transaction


def get_receipt(
    db: Session, *, user_id: uuid.UUID, transaction_id: uuid.UUID
) -> tuple[bytes, str]:
    transaction = get_transaction(db, user_id=user_id, transaction_id=transaction_id)
    if transaction.receipt_content_type is None:
        raise ReceiptNotFoundError
    return _receipt_path(transaction.id).read_bytes(), transaction.receipt_content_type


def delete_receipt(db: Session, *, user_id: uuid.UUID, transaction_id: uuid.UUID) -> Transaction:
    transaction = get_transaction(db, user_id=user_id, transaction_id=transaction_id)
    if transaction.receipt_content_type is None:
        raise ReceiptNotFoundError

    _receipt_path(transaction.id).unlink(missing_ok=True)
    transaction.receipt_content_type = None
    db.flush()
    return transaction
