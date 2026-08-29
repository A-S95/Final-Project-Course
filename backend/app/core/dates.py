from datetime import date


def add_months(day: date, months: int) -> date:
    """Devolve o **primeiro dia** do mês que está `months` meses à frente (ou atrás,
    se negativo) do mês de `day`. Usa aritmética de meses absolutos, por isso lida
    com viragens de ano em qualquer direção."""
    index = day.year * 12 + (day.month - 1) + months
    year, month = divmod(index, 12)
    return date(year, month + 1, 1)


def month_bounds(day: date) -> tuple[date, date]:
    """Primeiro dia do mês de `day` e primeiro dia do mês seguinte.

    Usa-se um intervalo semi-aberto [início, início_seguinte[ em vez de calcular o
    último dia do mês — evita ter de saber quantos dias tem cada mês. Partilhado
    pelo dashboard (Fase 6), pelos orçamentos (Fase 8) e pela analytics (Fase 11).
    """
    month_start = day.replace(day=1)
    return month_start, add_months(month_start, 1)
