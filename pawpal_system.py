# logic layer where the backend classes live


class Pet:
    def __init__(self, name: str, species: str, age: int):
        self.name = name
        self.species = species
        self.age = age

    def get_info(self) -> str:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int, pet: Pet):
        self.name = name
        self.available_minutes = available_minutes
        self.pet = pet


class CareTask:
    def __init__(self, title: str, duration_minutes: int, priority: str):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority

    def __repr__(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: list[CareTask] = []

    def add_task(self, task: CareTask):
        pass

    def generate_plan(self) -> list[CareTask]:
        pass

    def explain_plan(self) -> str:
        pass
