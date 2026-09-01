"""
Модуль парсинга расписания МИЭТ.
"""

import re
from datetime import datetime
from .consts import get_semester_start, SKIP_MILITARY


def compute_week_type(date_str: str) -> int:
    """
    Функция для вычисления типа недели 0-3 на основе даты и начала семестра.
    Формула: разница в днях % 28 // 7.
    Дата и начало семестра ожидаются в формате ДД.ММ.ГГГГ.
    """
    date = datetime.strptime(date_str, "%d.%m.%Y").date()
    semester_start = datetime.strptime(get_semester_start(), "%d.%m.%Y").date()
    delta = (date - semester_start).days
    if delta < 0:
        return 0
    return (delta % 28) // 7


def compute_week_number(date_str: str) -> int:
    """
    Функция для вычисления абсолютного номера недели, начиная с 1, на основе даты.
    """
    date = datetime.strptime(date_str, "%d.%m.%Y").date()
    semester_start = datetime.strptime(get_semester_start(), "%d.%m.%Y").date()
   
    delta = (date - semester_start).days
    if delta < 0:
        return 0
    
    return delta // 7 + 1


def get_week_type_string(week_type: int) -> str:
    """
    Функция для преобразования числового типа недели (0-3) в строку.
    """
    mapping = {
        0: "Числитель - 1",
        1: "Знаменатель - 1",
        2: "Числитель - 2",
        3: "Знаменатель - 2",
    }
    return mapping.get(week_type, "Неизвестно")


def get_week_info(date_str: str) -> dict:
    """
    Функция для получения информации о неделе для заданной даты:
    {
        "number": номер недели, начиная с 1,
        "type": числовой тип 0-3,
        "typeString": строковое представление
    }
    """
    week_type = compute_week_type(date_str)
    week_number = compute_week_number(date_str)
    type_string = get_week_type_string(week_type)
    return {
        "number": week_number,
        "type": week_type,
        "typeString": type_string
    }


def extract_lesson_type(name: str) -> tuple:
    """
    Функция для извлечения типа занятия из строки названия и получения очищенного названия и типа.
    Пример: "Ноксология [Лек]" -> ("Ноксология", "Лекция")
    Типы: Лек -> Лекция, Пр -> Практика, Сем -> Семинар, Лаб -> Лабораторная.
    Если тип не распознан, возвращается "Неизвестно".
    """
    match = re.search(r'\[(.*?)\]$', name)
    if not match:
        return name.strip(), "Неизвестно"

    type_code = match.group(1).strip()
    clean_name = re.sub(r'\s*\[.*?\]$', '', name).strip()

    type_map = {
        "Лек": "Лекция",
        "Пр": "Практика",
        "Сем": "Семинар",
        "Лаб": "Лабораторная",
    }
    lesson_type = type_map.get(type_code, "Неизвестно")

    return clean_name, lesson_type


def parse_time(time_str: str) -> str:
    """
    Функция для преобразования строки времени вида "0001-01-01T09:00:00" в формат "ЧЧ:ММ".
    """
    time_part = time_str.split('T')[1]
    return time_part[:-3]


def build_schedule_for_date(schedule_data: dict, target_date_str: str) -> dict:
    """
    Функция для преобразования сырых данных расписания в словарь из JSON
    в формате ДД.ММ.ГГГГ ведущие нули необязательны.
    Возвращает структурированный сортированный словарь.

    Если включён флаг SKIP_MILITARY и все занятия на эту дату являются
    "Военная подготовка", возвращается {дата: {}}, как бы "выходной".
    """
    target_date_obj = datetime.strptime(target_date_str, "%d.%m.%Y").date()
    formatted_date = target_date_obj.strftime("%d.%m.%Y")

    day_of_week = target_date_obj.isoweekday()
    week_type = compute_week_type(formatted_date)

    lessons = []
    for item in schedule_data.get("Data", []):
        if item.get("Day") == day_of_week and item.get("DayNumber") == week_type:
            lessons.append(item)

    if SKIP_MILITARY and lessons:
        all_military = all("Военная подготовка" in item["Class"]["Name"] for item in lessons)
        if all_military:
            return {formatted_date: {}}

    lessons.sort(key=lambda x: x["Time"]["Code"])

    result = {formatted_date: {}}
    for lesson in lessons:
        time_info = lesson["Time"]
        class_info = lesson["Class"]
        room_info = lesson["Room"]

        pair_number = time_info["Code"]
        time_from = parse_time(time_info["TimeFrom"])
        time_to = parse_time(time_info["TimeTo"])

        clean_title, lesson_type = extract_lesson_type(class_info["Name"])

        result[formatted_date][pair_number] = {
            "time": [time_from, time_to],
            "title": clean_title,
            "type": lesson_type,
            "full_name": class_info["TeacherFull"],
            "room": room_info["Name"]
        }

    return result
