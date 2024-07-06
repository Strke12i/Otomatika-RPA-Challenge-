from datetime import datetime
import re

class Utils:
    def format_date(self, date):
        if 'ago' in date: 
            return datetime.now().strftime("%m/%d/%Y")
        if '.' in date:
            date = date.replace('.', '')
        try:
            date_object = datetime.strptime(date, "%b %d, %Y")
        except ValueError:
            date_object = datetime.strptime(date, "%B %d, %Y")
        return date_object.strftime("%m/%d/%Y")
    
    def format_date_to_month_year(self, date):
        date_object = datetime.strptime(date, "%m/%d/%Y")
        return date_object.strftime("%m/%Y")
    
    def count_search_phrase(self, search_phrase, title, description):
        search_phrase = search_phrase.lower()
        return title.lower().count(search_phrase) + description.lower().count(search_phrase)
        
    def contains_money(self, title, description):
        money_pattern = r'\$[\d,.]+|\b\d+\s*(dollars|USD)\b'
        return bool(re.search(money_pattern, title, re.IGNORECASE) or re.search(money_pattern, description, re.IGNORECASE))
    
    def extract_num_pages(self, num_of_pages):
        return int(num_of_pages.split('of ')[1])
