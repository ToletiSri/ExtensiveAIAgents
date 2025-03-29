"""
Activity Planner Backend Package
This package provides functionality for task decomposition and execution.
"""

from .activity import decompose_task, execute_task
from .UtilityFunctions import (
    send_reminder_email,
    add_calendar_invite,
    send_stock_email,
    schedule_daily_stock_email
)

__all__ = [
    'decompose_task',
    'execute_task',
    'send_reminder_email',
    'add_calendar_invite',
    'send_stock_email',
    'schedule_daily_stock_email'
]
