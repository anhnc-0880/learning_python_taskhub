import logging

from app.models import Task, User

logger = logging.getLogger("taskhub")


def send_task_assigned_notification(task: Task, assignee: User) -> None:
    logger.info("Send assign notification to %s for task %s", assignee.email, task.title)
