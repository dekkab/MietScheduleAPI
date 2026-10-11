#!/usr/bin/env python3

"""
Пример использования библиотеки.
Выводит расписание на текущую неделю для рандомной группы.
"""

import random

from miet_schedule_api import get_current_week, get_groups_list

if __name__ == "__main__":
    try:
        groups = get_groups_list()
        if not groups:
            raise RuntimeError("Список групп пуст.")

        group = random.choice(groups)
        print(f"Случайная группа: {group}\n")

        schedule_json = get_current_week(
            group=group,
            force=False,
            return_json=True,
            pretty=True
        )
        print(schedule_json)
    
    except Exception as e:
        print(f"Ошибка: {e}")
