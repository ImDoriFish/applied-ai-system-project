from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class Task:
    description: str
    time: str                       # "HH:MM"
    frequency: str = "once"         # "once" | "daily" | "weekly"
    duration: int = 15              # minutes
    priority: str = "medium"        # "low" | "medium" | "high"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""              # set by Pet.add_task()

    def mark_complete(self) -> None: ...
    def update(self, field_name: str, value) -> None: ...


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None: ...
    def remove_task(self, task: Task) -> None: ...
    def get_tasks(self) -> List[Task]: ...


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None: ...
    def get_all_tasks(self) -> List[Task]: ...


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_todays_schedule(self) -> List[Task]: ...
    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]: ...
    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None) -> List[Task]: ...
    def detect_conflicts(self) -> List[str]: ...