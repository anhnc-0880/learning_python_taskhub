from datetime import datetime, date
from typing import List, Dict, Optional

class TaskRepository:
    def __init__(self):
        # Luu tam trong RAM vi chua hoc database
        self._tasks: Dict[int, dict] = {}
        self._current_id: int = 1

        # Seed data test
        self.create(
            project_id=1,
            task_data={
                "title": "Setup skeleton app",
                "description": "Tao project setup layered architecture",
                "status": "DONE",
                "priority": "HIGH",
                "due_date": date(2026, 7, 13),
                "assignee_id": 1
            },
            created_by=1
        )

    def get_by_project(self, project_id: int) -> List[dict]:
        return [task for task in self._tasks.values() if task["project_id"] == project_id]

    def get_by_id(self, task_id: int) -> Optional[dict]:
        return self._tasks.get(task_id)

    def create(self, project_id: int, task_data: dict, created_by: int) -> dict:
        new_task = {
            "id": self._current_id,
            "project_id": project_id,
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat() + "Z",
            **task_data
        }
        if isinstance(new_task.get("due_date"), date):
            new_task["due_date"] = new_task["due_date"].isoformat()
            
        self._tasks[self._current_id] = new_task
        self._current_id += 1
        return new_task

    def update(self, task_id: int, task_data: dict) -> Optional[dict]:
        if task_id not in self._tasks:
            return None
        
        if "due_date" in task_data and isinstance(task_data["due_date"], date):
            task_data["due_date"] = task_data["due_date"].isoformat()

        self._tasks[task_id].update(task_data)
        return self._tasks[task_id]

    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
