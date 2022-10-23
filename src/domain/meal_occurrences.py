from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class MealOccurrences:
    meal_id: str
    name: Optional[str] = None
    total: int = 0
    l: int = 0
    g: int = 0
    both: int = 0
   
    def __post_init__(self):
        self.total = self.l + self.g + self.both
