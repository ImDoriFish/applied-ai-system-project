"""PawPal+ logic layer: Task, Pet, Owner, and Scheduler classes."""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


def validate_time(value: str) -> None:
    """Raise a ValueError unless value is a 24-hour 'HH:MM' time like '09:00'."""
    message = f"Invalid time '{value}'. Use 24-hour HH:MM format, e.g. '09:00'."
    if not isinstance(value, str) or len(value) != 5 or value[2] != ":":
        raise ValueError(message)
    hour, minute = value[:2], value[3:]
    if not (hour.isdigit() and minute.isdigit()):
        raise ValueError(message)
    if int(hour) > 23 or int(minute) > 59:
        raise ValueError(message)


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str                       # "HH:MM"
    frequency: str = "once"         # "once" | "daily" | "weekly"
    duration: int = 15              # minutes
    priority: str = "medium"        # "low" | "medium" | "high"
    due_date: date = field(default_factory=date.today)
    completed: bool = False
    pet_name: str = ""              # set by Pet.add_task()

    def __post_init__(self) -> None:
        """Validate the time as soon as a Task is created."""
        validate_time(self.time)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def update(self, field_name: str, value) -> None:
        """Change one editable field of this task (completion is not editable here)."""
        if field_name == "description":
            self.description = value
        elif field_name == "time":
            validate_time(value)
            self.time = value
        elif field_name == "frequency":
            self.frequency = value
        elif field_name == "duration":
            self.duration = value
        elif field_name == "priority":
            self.priority = value
        elif field_name == "due_date":
            self.due_date = value
        else:
            raise ValueError("Invalid field name")

@dataclass
class Pet:
    """A pet and the list of tasks that belong to it."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and stamp it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet if it exists."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> List[Task]:
        """Return this pet's list of tasks."""
        return self.tasks


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name, or return None if not found."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return every task from all of this owner's pets in one list."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    """The 'brain' that organizes tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Store the owner whose pets' tasks this scheduler manages."""
        self.owner = owner

    def get_todays_schedule(self) -> List[Task]:
        """Return today's tasks for all pets, sorted by time."""
        todays = self.filter_tasks(day=date.today())
        return self.sort_tasks(todays, by="time")

    def sort_tasks(self, tasks: List[Task], by: str = "time") -> List[Task]:
        """Return tasks sorted by time, priority (then time), or duration."""
        if by == "time":
            return sorted(tasks, key=lambda t: t.time)
        if by == "priority":
            rank = {"high": 0, "medium": 1, "low": 2}
            return sorted(tasks, key=lambda t: (rank.get(t.priority, 3), t.time))
        if by == "duration":
            return sorted(tasks, key=lambda t: t.duration)
        raise ValueError(f"Cannot sort by '{by}'")

    def filter_tasks(self, pet_name: Optional[str] = None,
                     completed: Optional[bool] = None,
                     day: Optional[date] = None) -> List[Task]:
        """Return tasks matching any combination of pet name, completion status, and day."""
        result = []
        for task in self.owner.get_all_tasks():
            if pet_name is not None and task.pet_name != pet_name:
                continue
            if completed is not None and task.completed != completed:
                continue
            if day is not None and task.due_date != day:
                continue
            result.append(task)
        return result

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for unfinished tasks sharing the same date and time."""
        slots = {}
        for task in self.owner.get_all_tasks():
            if task.completed:
                continue
            key = (task.due_date, task.time)
            if key not in slots:
                slots[key] = []
            slots[key].append(task)

        warnings = []
        for (day, time), tasks in slots.items():
            if len(tasks) > 1:
                names = ", ".join(f"{t.description} ({t.pet_name})" for t in tasks)
                warnings.append(f"Conflict on {day} at {time}: {names}")
        return warnings

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task and create its next occurrence if it repeats daily or weekly."""
        if task.completed:
            return None
        task.mark_complete()

        if task.frequency == "daily":
            next_date = task.due_date + timedelta(days=1)
        elif task.frequency == "weekly":
            next_date = task.due_date + timedelta(days=7)
        else:
            return None

        next_task = Task(
            description=task.description,
            time=task.time,
            frequency=task.frequency,
            duration=task.duration,
            priority=task.priority,
            due_date=next_date,
        )
        pet = self.owner.get_pet(task.pet_name)
        if pet is not None:
            pet.add_task(next_task)
        return next_task
