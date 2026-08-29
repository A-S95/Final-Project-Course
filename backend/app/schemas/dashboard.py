import enum
import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class DashboardScope(enum.StrEnum):
    INDIVIDUAL = "individual"
    HOUSEHOLD = "household"


class CategoryExpense(BaseModel):
    """Total gasto numa categoria de despesa dentro do mês selecionado.

    Na vista de agregado, uma linha representa ou uma despesa partilhada
    (fundida entre todos os membros que a marcaram — `owner_name` é `None`,
    porque já não pertence a uma pessoa só) ou a despesa pessoal de um único
    membro (`owner_name` identifica de quem é, para não confundir com a
    despesa homónima de outro membro). Na vista individual `owner_name` é
    sempre `None` — só há uma pessoa, não há nada a desambiguar.
    """

    category_id: uuid.UUID
    name: str
    color: str | None
    total: Decimal
    owner_name: str | None = None


class DashboardSummary(BaseModel):
    # Primeiro dia do mês a que o resumo diz respeito (ex: 2026-08-01) — a UI
    # navega entre meses passando este valor de volta.
    month: date
    # Qual a vista devolvida. Se pediram "household" mas o utilizador não pertence
    # a um agregado, o service devolve os dados individuais e marca "individual".
    scope: DashboardScope
    # Soma dos `current_balance` de todas as contas incluídas na vista. Não é do
    # mês: é a fotografia "agora", independente do mês escolhido.
    total_balance: Decimal
    # Receitas/despesas do mês. Transferências entre contas próprias nunca entram
    # nestes totais (ver ARCHITECTURE.md secção 8) — só movem saldos.
    total_income: Decimal
    total_expenses: Decimal
    # total_income - total_expenses (pode ser negativo).
    net: Decimal
    # (net / total_income) * 100, arredondado a 1 casa. `None` quando não houve
    # receitas no mês (divisão por zero não tem significado útil). É um rácio para
    # exibição, não um valor monetário — daí `float` e não `Decimal`.
    savings_rate: float | None
    # Despesas do mês agrupadas por categoria, da maior para a menor.
    expenses_by_category: list[CategoryExpense]
    # Quanto de `total_expenses` está marcado como despesa partilhada do
    # agregado (`Transaction.is_shared`). Só relevante na vista "household";
    # na vista individual reflete só as despesas que a própria pessoa marcou.
    shared_expenses_total: Decimal
