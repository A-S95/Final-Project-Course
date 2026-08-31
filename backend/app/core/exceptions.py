class DomainError(Exception):
    """Erro de regra de negócio. O handler em `app/main.py` traduz qualquer
    subclasse numa resposta HTTP usando `status_code` e `detail` — os routers não
    precisam de apanhar nada, só chamam o serviço e fazem `db.commit()`.

    Erros cuja mensagem depende do contexto (validação de combinações de campos)
    passam o texto ao construtor; os restantes definem `detail` como atributo de
    classe.
    """

    status_code: int = 400
    detail: str = "Pedido inválido."

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


# --- Autenticação ---


class EmailAlreadyRegisteredError(DomainError):
    status_code = 409
    detail = "Já existe uma conta com este email."


class InvalidCredentialsError(DomainError):
    status_code = 401
    detail = "Email ou password inválidos."


class InvalidRefreshTokenError(DomainError):
    status_code = 401
    detail = "Refresh token inválido ou expirado."


class RefreshTokenRaceError(DomainError):
    """Refresh token já rodado, reapresentado dentro da janela de tolerância: pedido
    concorrente benigno (mesmo cookie enviado 2x), não roubo. Falha só este pedido,
    sem revogar a família de tokens. Tratado explicitamente em `auth.py` (mexe no cookie)."""

    status_code = 409
    detail = "Sessão a ser renovada noutro pedido — tenta novamente."


class InvalidPasswordResetTokenError(DomainError):
    status_code = 400
    detail = "Ligação de recuperação inválida ou expirada. Pede uma nova."


# --- Contas ---


class AccountNotFoundError(DomainError):
    status_code = 404
    detail = "Conta não encontrada."


class AccountInUseError(DomainError):
    status_code = 409
    detail = (
        "Esta conta está a ser usada (transações ou despesas recorrentes) e não pode ser eliminada."
    )


# --- Categorias ---


class CategoryNotFoundError(DomainError):
    status_code = 404
    detail = "Categoria não encontrada."


class CategoryNameAlreadyExistsError(DomainError):
    status_code = 409
    detail = "Já existe uma categoria com este nome."


class CategoryInUseError(DomainError):
    status_code = 409
    detail = (
        "Esta categoria está a ser usada (transações, orçamentos ou despesas recorrentes) e "
        "não pode ser eliminada."
    )


class InvalidCategoryReassignError(DomainError):
    """Categoria de destino da reatribuição inválida (igual à original, inexistente,
    ou de tipo diferente)."""

    status_code = 422


# --- Transações ---


class TransactionNotFoundError(DomainError):
    status_code = 404
    detail = "Transação não encontrada."


class InvalidTransactionError(DomainError):
    """Combinação de campos inválida para o tipo de transação (ex: transferência com
    categoria, receita sem categoria, conta de destino igual à de origem)."""

    status_code = 422


class ReceiptNotFoundError(DomainError):
    status_code = 404
    detail = "Esta transação não tem recibo."


class InvalidReceiptError(DomainError):
    """Ficheiro de recibo inválido (tipo não suportado ou demasiado grande)."""

    status_code = 422


# --- Orçamentos ---


class BudgetNotFoundError(DomainError):
    status_code = 404
    detail = "Orçamento não encontrado."


class BudgetAlreadyExistsError(DomainError):
    status_code = 409
    detail = "Já existe um orçamento para esta categoria neste mês."


class BudgetCategoryInvalidError(DomainError):
    status_code = 422
    detail = "Só categorias de despesa podem ter orçamento."


# --- Objetivos ---


class GoalNotFoundError(DomainError):
    status_code = 404
    detail = "Objetivo não encontrado."


class InvalidGoalContributionError(DomainError):
    status_code = 422
    detail = "A contribuição deixaria o objetivo com um valor acumulado negativo."


# --- Despesas recorrentes ---


class RecurringExpenseNotFoundError(DomainError):
    status_code = 404
    detail = "Despesa recorrente não encontrada."


class RecurringExpenseCategoryInvalidError(DomainError):
    status_code = 422
    detail = "Uma despesa recorrente tem de usar uma categoria de despesa."


# --- Agregado familiar ---


class AlreadyInHouseholdError(DomainError):
    status_code = 409
    detail = "Já pertences a um agregado familiar."


class NotInHouseholdError(DomainError):
    status_code = 404
    detail = "Não pertences a nenhum agregado familiar."


class InvitedUserNotFoundError(DomainError):
    status_code = 404
    detail = "Não existe nenhum utilizador com esse email."


class HouseholdInviteNotFoundError(DomainError):
    status_code = 404
    detail = "Convite não encontrado."


class InvalidHouseholdInviteError(DomainError):
    """Convite inválido no contexto atual (a si próprio, a quem já é membro, a quem
    já está noutro agregado, convite duplicado pendente, ou convite já respondido)."""

    status_code = 409
