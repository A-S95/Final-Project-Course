class EmailAlreadyRegisteredError(Exception):
    """Já existe um utilizador com este email."""


class InvalidCredentialsError(Exception):
    """Email ou password não correspondem a um utilizador válido."""


class InvalidRefreshTokenError(Exception):
    """Refresh token inexistente, revogado ou expirado."""


class AccountNotFoundError(Exception):
    """Conta inexistente ou não pertence ao utilizador autenticado."""


class CategoryNotFoundError(Exception):
    """Categoria inexistente ou não pertence ao utilizador autenticado."""


class CategoryNameAlreadyExistsError(Exception):
    """Já existe uma categoria com este nome para este utilizador (UNIQUE(user_id, name))."""


class AccountInUseError(Exception):
    """Conta tem transações associadas — não pode ser eliminada (FK ON DELETE RESTRICT)."""


class CategoryInUseError(Exception):
    """Categoria tem transações associadas — não pode ser eliminada (FK ON DELETE RESTRICT)."""


class InvalidCategoryReassignError(Exception):
    """Categoria de destino da reatribuição inválida (igual à original, inexistente,
    ou de tipo diferente — receita/despesa)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class TransactionNotFoundError(Exception):
    """Transação inexistente ou não pertence ao utilizador autenticado."""


class BudgetNotFoundError(Exception):
    """Orçamento inexistente ou não pertence ao utilizador autenticado."""


class BudgetAlreadyExistsError(Exception):
    """Já existe um orçamento para esta categoria neste mês (UNIQUE(user, categoria, mês))."""


class BudgetCategoryInvalidError(Exception):
    """A categoria indicada não é de despesa — só categorias EXPENSE têm orçamento."""


class GoalNotFoundError(Exception):
    """Objetivo inexistente ou não pertence ao utilizador autenticado."""


class InvalidGoalContributionError(Exception):
    """A contribuição deixaria o valor acumulado do objetivo negativo."""


class RecurringExpenseNotFoundError(Exception):
    """Despesa recorrente inexistente ou não pertence ao utilizador autenticado."""


class RecurringExpenseCategoryInvalidError(Exception):
    """A categoria indicada não é de despesa — uma despesa recorrente é sempre EXPENSE."""


class AlreadyInHouseholdError(Exception):
    """O utilizador já pertence a um agregado familiar (só se pode pertencer a um)."""


class NotInHouseholdError(Exception):
    """O utilizador não pertence a nenhum agregado familiar."""


class InvitedUserNotFoundError(Exception):
    """Não existe nenhum utilizador registado com o email indicado no convite."""


class HouseholdInviteNotFoundError(Exception):
    """Convite inexistente, ou não dirigido/pertencente ao utilizador autenticado."""


class InvalidHouseholdInviteError(Exception):
    """Convite inválido no contexto atual (a si próprio, a quem já é membro, a quem
    já está noutro agregado, convite duplicado pendente, ou convite já respondido)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvalidTransactionError(Exception):
    """Combinação de campos inválida para o tipo de transação (ex: transferência com
    categoria, receita sem categoria, conta de destino igual à de origem)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ReceiptNotFoundError(Exception):
    """A transação existe mas não tem nenhum recibo anexado."""


class InvalidReceiptError(Exception):
    """Ficheiro de recibo inválido (tipo não suportado ou demasiado grande)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
