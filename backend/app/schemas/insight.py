import enum

from pydantic import BaseModel


class InsightSeverity(enum.StrEnum):
    WARNING = "warning"  # merece atenção
    INFO = "info"  # observação neutra
    POSITIVE = "positive"  # boa notícia


class Insight(BaseModel):
    # Id estável da regra (ex: "budget_exceeded") — permite à UI dar-lhe um ícone
    # fixo e ao utilizador reconhecer o mesmo tipo de alerta entre meses.
    rule: str
    severity: InsightSeverity
    title: str
    detail: str
