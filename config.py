from RPA.Robocorp.WorkItems import WorkItems
import datetime
import math

class Config:
    def __init__(self):
        try:
            wi = WorkItems()
            wi.get_input_work_item()
            self.url = wi.get_work_item_variable("url")
            self.topic = wi.get_work_item_variable("topic")
            self.search_phrase = wi.get_work_item_variable("search_phrase")
            self.period = wi.get_work_item_variable("period")
        except Exception as e:
            print(f"Error: {e}")
            raise e
        
    def get_period(self):
        """
            Example of how this should work: 
            0 or 1 - only the current month, 2 - current and previous month, 3 - 
            current and two previous months, and so on
        """
        date = datetime.datetime.now()
        month = date.month
        year = date.year
        
        if self.period == 0 or self.period == 1:
            return [f"{month:02}/{year}"]
        
        periods = []
        for i in range(self.period):
            if month == 0:
                month = 12
                year -= 1
            periods.append(f"{month:02}/{year}")
            month -= 1
            
        return periods