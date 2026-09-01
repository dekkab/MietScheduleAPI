"""
Небольшая библиотека для получения расписания групп МИЭТ.
"""

from .core import (
    get_schedule,
    get_schedule_range,
    get_current_week,
    get_next_week,
    get_previous_week,
    fetch_schedule,
    get_groups_list,
    validate_group,
    load_cached_data,
    save_cached_data,
    set_semester_start,
    set_skip_military,
)

__version__ = "0.1.0"
__all__ = [
    "get_schedule",
    "get_schedule_range",
    "get_current_week",
    "get_next_week",
    "get_previous_week",
    "fetch_schedule",
    "get_groups_list",
    "validate_group",
    "load_cached_data",
    "save_cached_data",
    "set_semester_start",
    "set_skip_military",
]
