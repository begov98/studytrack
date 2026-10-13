"""Бизнес логика и валидация на учебните задачи."""

import re
from datetime import datetime


def validate_task(title: str, subject: str, due_date: str) -> dict:
    """Проверява данните и връща подготвени стойности за запис."""
    title = title.strip()
    subject = subject.strip()
    due_date = due_date.strip()

    if not title:
        raise ValueError("Въведи заглавие на задачата.")

    if not subject:
        raise ValueError("Въведи предмет.")

    if not due_date:
        raise ValueError("Въведи краен срок.")

    if not re.fullmatch(r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}", due_date):
        raise ValueError("Въведи датата във формат ДД.ММ.ГГГГ.")

    try:
        parsed_date = datetime.strptime(due_date, "%d.%m.%Y").date()
    except ValueError:
        raise ValueError("Въведи валидна календарна дата.") from None

    return {
        "title": title,
        "subject": subject,
        "due_date": parsed_date.isoformat(),
    }