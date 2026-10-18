from pawpal_system import Owner, Pet, Task, Scheduler


def print_tasks(title, tasks):
    print(f"\n{title}")
    print("-" * 40)
    if not tasks:
        print("  (no tasks)")
    for t in tasks:
        status = "✓" if t.completed else " "
        print(f"  [{status}] {t.time}  {t.description:<14} {t.pet_name:<8} {t.priority}")


owner = Owner("Jordan")
mochi = Pet("Mochi", "dog")
biscuit = Pet("Biscuit", "cat")
owner.add_pet(mochi)
owner.add_pet(biscuit)

# Added out of order on purpose, to show sorting works
mochi.add_task(Task("Evening walk", "18:00", priority="medium", duration=30))
mochi.add_task(Task("Breakfast", "08:00", frequency="daily", priority="high", duration=10))
biscuit.add_task(Task("Litter box", "09:00", priority="low", duration=5))
mochi.add_task(Task("Vet visit", "09:00", priority="high", duration=60))   # same time -> conflict

scheduler = Scheduler(owner)

print_tasks("Today's Schedule", scheduler.get_todays_schedule())
print_tasks("Sorted by priority", scheduler.sort_tasks(owner.get_all_tasks(), by="priority"))
print_tasks("Mochi's tasks only", scheduler.filter_tasks(pet_name="Mochi"))

print("\nConflicts")
print("-" * 40)
for warning in scheduler.detect_conflicts():
    print(f"  ⚠ {warning}")

breakfast = mochi.get_tasks()[1]
next_task = scheduler.mark_task_complete(breakfast)
print(f"\nCompleted '{breakfast.description}'. Next one created for {next_task.due_date}.")
print_tasks("Pending tasks", scheduler.filter_tasks(completed=False))