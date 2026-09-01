"""
Основной модуль библиотеки для получения расписания.
Предоставляет функции для загрузки, кэширования и парсинга расписания.
"""

import json
import os
import requests
from datetime import datetime, timedelta
from .consts import API_URL, GROUPS_URL, TOTAL_WEEKS, SKIP_MILITARY, get_semester_start, set_semester_start
from .parser import build_schedule_for_date, get_week_info

def get_groups_list() -> list:
    """
    Функция для получения списка всех доступных групп из API.
    """
    try:
        response = requests.get(GROUPS_URL)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ошибка при получении списка групп: {e}")


def validate_group(group: str) -> bool:
    """
    Функция для проверки, существует ли указанная группа.
    """
    groups = get_groups_list()
    return group in groups


def fetch_schedule(group: str) -> dict:
    """
    Функция для выполнения POST-запроса к API расписания и получения самого расписания в виде JSON-ответа.
    """
    try:
        response = requests.post(API_URL, data={"group": group})
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ошибка при запросе расписания для группы {group}: {e}")


def load_cached_data(group: str) -> dict | None:
    """
    Функция для загрузки данных для указанной группы из единого файла кэша.
    Возвращает словарь с данными расписания или None, если группа не найдена.
    """
    cache_path = "last_data.json"
    if not os.path.exists(cache_path):
        return None
    
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            all_data = json.load(f)
        return all_data.get(group)
    
    except (json.JSONDecodeError, IOError):
        return None


def save_cached_data(group: str, data: dict):
    """
    Функция для сохранения данных для указанной группы в единый файл кэша.
    Если файл существует, обновляет запись для группы, иначе, создаёт новый.
    """
    cache_path = "last_data.json"
    all_data = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        
        except (json.JSONDecodeError, IOError):
            all_data = {}
    
    all_data[group] = data
    
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)


def get_schedule(group: str, date_str: str, force: bool = False, return_json: bool = False, pretty: bool = False):
    """
    Функция для получения структурированного расписания для указанной группы и даты.

    Аргументы:
        group: код группы / обязательный параметр
        date_str: дата в формате ДД.ММ.ГГГГ
        force: если True, принудительно запрашивает данные с сервера
        return_json: если True, возвращает строку JSON, иначе словарь
        pretty: если True, форматирует JSON с отступами; работает только при return_json=True

    Возвращает словарь или строку JSON.
    """
    if not validate_group(group):
        raise ValueError(f"Группа '{group}' не найдена в списке доступных групп.")

    is_from_cache = False
    schedule_data = None

    if not force:
        cached = load_cached_data(group)
        if cached is not None:
            schedule_data = cached
            is_from_cache = True
        
        else:
            schedule_data = fetch_schedule(group)
            save_cached_data(group, schedule_data)
    
    else:
        schedule_data = fetch_schedule(group)
        save_cached_data(group, schedule_data)

    if schedule_data is None:
        raise RuntimeError(f"Не удалось получить данные расписания для группы {group}.")

    result_data = build_schedule_for_date(schedule_data, date_str)

    week_info = get_week_info(date_str)
    meta = {
        "weeks": {date_str: week_info},
        "total_weeks": TOTAL_WEEKS
    }

    result = {
        "isFromCache": is_from_cache,
        "data": result_data,
        "meta": meta
    }

    if return_json:
        indent = 2 if pretty else None
        return json.dumps(result, ensure_ascii=False, indent=indent)
    
    return result


def get_schedule_range(group: str, start_date_str: str, end_date_str: str, force: bool = False, return_json: bool = False, pretty: bool = False):
    """
    Функция для получения структурированного расписания для указанной группы и диапазона дат.

    Аргументы:
        group: код группы / обязательный параметр
        start_date_str: начальная дата в формате ДД.ММ.ГГГГ
        end_date_str: конечная дата в формате ДД.ММ.ГГГГ
        force: если True, принудительно запрашивает данные с сервера
        return_json: если True, возвращает строку JSON, иначе словарь
        pretty: если True, форматирует JSON с отступами; работает только при return_json=True

    Возвращает словарь или строку JSON.
    """
    if not validate_group(group):
        raise ValueError(f"Группа '{group}' не найдена в списке доступных групп.")

    start = datetime.strptime(start_date_str, "%d.%m.%Y")
    end = datetime.strptime(end_date_str, "%d.%m.%Y")
    if start > end:
        start, end = end, start

    is_from_cache = False
    schedule_data = None

    if not force:
        cached = load_cached_data(group)
        if cached is not None:
            schedule_data = cached
            is_from_cache = True
        
        else:
            schedule_data = fetch_schedule(group)
            save_cached_data(group, schedule_data)
    
    else:
        schedule_data = fetch_schedule(group)
        save_cached_data(group, schedule_data)

    if schedule_data is None:
        raise RuntimeError(f"Не удалось получить данные расписания для группы {group}.")

    result_data = {}
    weeks_info = {}
    current = start
    delta = timedelta(days=1)
    while current <= end:
        date_str = current.strftime("%d.%m.%Y")
        day_result = build_schedule_for_date(schedule_data, date_str)
        result_data.update(day_result)
        weeks_info[date_str] = get_week_info(date_str)
        current += delta

    meta = {
        "weeks": weeks_info,
        "total_weeks": TOTAL_WEEKS
    }

    result = {
        "isFromCache": is_from_cache,
        "data": result_data,
        "meta": meta
    }

    if return_json:
        indent = 2 if pretty else None
        return json.dumps(result, ensure_ascii=False, indent=indent)
    
    return result


def get_current_week(group: str, date_str: str = None, force: bool = False, return_json: bool = False, pretty: bool = False):
    """
    Функция для получения расписания на текущую неделю / с понедельника по воскресенье,
    относительно заданной даты или текущей даты, если date_str не указан.

    Аргументы:
        group: код группы / обязательный параметр
        date_str: опционально, дата в формате ДД.ММ.ГГГГ, от которой вычисляется неделя; если не указана, используется сегодняшняя дата
        force: если True, принудительно запрашивает данные с сервера
        return_json: если True, возвращает строку JSON, иначе словарь
        pretty: если True, форматирует JSON с отступами

    Возвращает словарь или строку JSON с расписанием на неделю.
    """
    if date_str is None:
        date_str = datetime.now().strftime("%d.%m.%Y")
    dt = datetime.strptime(date_str, "%d.%m.%Y")
    start_of_week = dt - timedelta(days=dt.weekday())  # понедельник
    end_of_week = start_of_week + timedelta(days=6)
    start_str = start_of_week.strftime("%d.%m.%Y")
    end_str = end_of_week.strftime("%d.%m.%Y")
    return get_schedule_range(group, start_str, end_str, force, return_json, pretty)


def get_next_week(group: str, date_str: str = None, force: bool = False, return_json: bool = False, pretty: bool = False):
    """
    Функция для получения расписания на следующую неделю / с понедельника по воскресенье
    относительно заданной даты или текущей даты, если date_str не указан.

    Аргументы:
        group: код группы / обязательный параметр
        date_str: опционально, дата в формате ДД.ММ.ГГГГ, от которой вычисляется неделя; если не указана, используется сегодняшняя дата
        force: если True, принудительно запрашивает данные с сервера
        return_json: если True, возвращает строку JSON, иначе словарь
        pretty: если True, форматирует JSON с отступами

    Возвращает словарь или строку JSON с расписанием на неделю.
    """
    if date_str is None:
        date_str = datetime.now().strftime("%d.%m.%Y")
    dt = datetime.strptime(date_str, "%d.%m.%Y")
    start_of_week = dt - timedelta(days=dt.weekday()) + timedelta(days=7)
    end_of_week = start_of_week + timedelta(days=6)
    start_str = start_of_week.strftime("%d.%m.%Y")
    end_str = end_of_week.strftime("%d.%m.%Y")
    return get_schedule_range(group, start_str, end_str, force, return_json, pretty)

def get_previous_week(group: str, date_str: str = None, force: bool = False, return_json: bool = False, pretty: bool = False):
    """
    Метод для получения расписания на предыдущую неделю / с понедельника по воскресенье
    относительно заданной даты или текущей даты, если date_str не указан.

    Аргументы:
        group: код группы / обязательный параметр
        date_str: опционально, дата в формате ДД.ММ.ГГГГ, от которой вычисляется неделя; если не указана, используется сегодняшняя дата
        force: если True, принудительно запрашивает данные с сервера
        return_json: если True, возвращает строку JSON, иначе словарь
        pretty: если True, форматирует JSON с отступами

    Возвращает словарь или строку JSON с расписанием на неделю.
    """
    if date_str is None:
        date_str = datetime.now().strftime("%d.%m.%Y")
    
    dt = datetime.strptime(date_str, "%d.%m.%Y")
    start_of_week = dt - timedelta(days=dt.weekday()) - timedelta(days=7)
    end_of_week = start_of_week + timedelta(days=6)
    start_str = start_of_week.strftime("%d.%m.%Y")
    end_str = end_of_week.strftime("%d.%m.%Y")
    
    return get_schedule_range(group, start_str, end_str, force, return_json, pretty)


def get_semester_start():
    """Возвращает дату начала семестра."""
    from .consts import get_semester_start as _get
    return _get()


def set_semester_start(new_start: str):
    """Устанавливает дату начала семестра."""
    from .consts import set_semester_start as _set
    _set(new_start)


def set_skip_military(value: bool):
    """Включает или выключает пропуск дней военной подготовки."""
    global SKIP_MILITARY
    SKIP_MILITARY = value
