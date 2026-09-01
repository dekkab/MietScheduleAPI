"""
Константы для скрипта расписания.
"""

from datetime import datetime


# URL API расписания МИЭТ
API_URL = "https://miet.ru/schedule/data"

# URL API списка групп
GROUPS_URL = "https://miet.ru/schedule/groups"

# Общее количество недель в семестре
TOTAL_WEEKS = 20

# Если истина, дни, состоящие только из занятий "Военная подготовка",
# будут считаться свободными и возвращаться как {}
SKIP_MILITARY = True

# Внутренняя переменная для хранения даты начала семестра
_SEMESTER_START = None


def get_semester_start() -> str:
    """
    Функция для возврата даты начала семестра в формате ДД.ММ.ГГГГ.
    Если дата не была установлена явно через сеттер,
    она вычисляется автоматически на основе текущей даты:
    - если текущий месяц >= 9 (сентябрь), то год текущий,
    - иначе год предыдущий.
    """
    
    global _SEMESTER_START
    if _SEMESTER_START is None:
        _CURRENT_YEAR = datetime.now().year
        _CURRENT_MONTH = datetime.now().month
        if _CURRENT_MONTH >= 9:
            _SEMESTER_START = f"01.09.{_CURRENT_YEAR}"
        
        else:
            _SEMESTER_START = f"01.09.{_CURRENT_YEAR - 1}"
    
    return _SEMESTER_START


def set_semester_start(new_start: str):
    """
    Явно устанавливает дату начала семестра в формате ДД.ММ.ГГГГ.
    """
    global _SEMESTER_START
    _SEMESTER_START = new_start


# Для обратной совместимости сохраняем константу, но она теперь вычисляется при первом обращении
SEMESTER_START = get_semester_start()
