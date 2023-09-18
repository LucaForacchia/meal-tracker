from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class Meal:
    date: datetime
    # meal_type and participants could also be an enum ?
    meal_type: str
    participants: str

    meal : str
    notes : str
   
    start_week: bool = False
    week_number: Optional[int] = None

    timestamp: int = 0
    meal_id: str = ""
    dessert: Optional[str] = None
   
    def __post_init__(self):
        if self.timestamp == 0:
            offset = 12*60*60 if self.meal_type == "Pranzo" else 20*60*60
            self.timestamp = self.date.timestamp() + offset
        self.meal_id = self.build_meal_id()
        self.date = self.date.date().isoformat()
       
    def build_meal_id(self):
        return str(self.meal).upper().replace(" E ", "").replace(",", "").replace(" ","")