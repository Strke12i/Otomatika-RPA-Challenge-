from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.Robocorp.WorkItems import WorkItems
from util import Utils
import logging
import uuid
import os
import requests
import glob


utils = Utils()
logging.basicConfig(filename='./output/robot.log', level=logging.INFO)

class Scrapper:
    def __init__(self, url, topic, search_phrase, period):
        self.url = url
        self.topic = topic
        self.search_phrase = search_phrase
        self.period = period
        self.page_count = 1
        self.max_pages = 10 
        self.news_list = []
        self.browser = Selenium()
        self.excel = Files()

    def open_browser(self):
        self.browser.open_available_browser(self.url)
        
    def search_news(self):
        """Search news on the website using the search phrase from working item
        """
        try: 
            button_locator = 'xpath://button[@data-element="search-button"]'
            self.browser.click_button(button_locator)
            
            input_locator = 'xpath://input[@data-element="search-form-input"]'
            self.browser.input_text(input_locator, self.search_phrase)
            
            button_submit_locator = 'xpath://button[@data-element="search-submit-button"]'
            self.browser.click_button(button_submit_locator)
            
        except Exception as e:
            logging.error(f"Error: {e}")
            
    def load_news(self):
        """
            Wait until the news are loaded on the page
        """
        ul_locator = 'css:ul.search-results-module-results-menu'
        self.browser.wait_until_element_is_visible(ul_locator)
        logging.info("Loading news...")
    
    def click_filter(self):
        """
            Click on the filter button to set the topic
        """
        try:
            button_locator = 'css:button.button filters-open-button'
            if self.browser.is_element_visible(button_locator):
                self.browser.click_button(button_locator)
            else:
                logging.warning("Filter button not found")
                pass
        except Exception as e:
            raise Exception(f"Error: {e}")
        
    def get_element_value(self, locator):
        """
            Get the text from the element    
        """
        if self.browser.is_element_visible(locator):
            return self.browser.get_text(locator)
        return None
    
    def set_filter(self):
        try:
            self.click_filter()
            
            see_all_button_locator = 'xpath://button[@class="button see-all-button" and @data-toggle-trigger="see-all"]'
            self.browser.click_button(see_all_button_locator)

            labels_locator = '//label[@class="checkbox-input-label"]'
            self.browser.wait_until_element_is_visible(labels_locator)
            
            labels = self.browser.get_webelements(labels_locator)
            for label in labels:
                try:
                    label_text = label.text
                    if self.topic.lower() in label_text.lower():
                        self.browser.click_element(label)
                        break
                    
                except Exception as e:
                    logging.error(f"Error: {e}")
        except Exception as e:
            logging.error(f"Error on set_filter: {e}")
    
    def sort_by_newest(self):
        try:
            locator_input = 'xpath://select[@class="select-input"]'
            self.browser.select_from_list_by_value(locator_input, "1")
            self.browser.wait_until_page_contains_element('xpath://option[@value="1" and @selected="selected"]')
            return True
        except Exception as e:
            logging.error(f"Error: {e}")
            return False
    
    def get_element_value(self, locator):
        try: 
            if self.browser.is_element_visible(locator):
                return self.browser.get_text(locator)
            return None
        except Exception as e:
            logging.error(f"Error: {e}")
            return None
    
    def go_to_next_page(self):
        try:
            button_locator = '//div[@class="search-results-module-next-page"]'
            self.browser.wait_until_element_is_visible(button_locator)
            if self.browser.is_element_visible(button_locator):
                div = self.browser.get_webelement(button_locator)
                
                enabled = div.find_element("tag name", "svg")
                if self.browser.get_element_attribute(enabled, "data-inactive"):
                    return False
                
                self.browser.click_element(div)
                
                return True
            return False
        except Exception as e:
            logging.error(f"Error on go_to_next_page: {e}")
            return False
        
            
    def find_element(self, li, identifier, value):
        try:
            return li.find_element(identifier, value).text
        except Exception as e:
            logging.error(f"Error on find_element: {e}")
            return ''
            
    def find_image(self, li):
        try:
            return li.find_element("tag name", "img").get_attribute("src")
        except Exception as e:
            logging.error(f"Error on find_image: {e}")
            return ''
            
    def get_max_pages(self):
        try:
            self.browser.wait_until_element_is_visible('css:div.search-results-module-page-counts')
            div_locator = '//div[@class="search-results-module-page-counts"]'
            num_of_pages = self.browser.get_text(div_locator)
            num_of_pages = utils.extract_num_pages(num_of_pages)
            if num_of_pages < self.max_pages:
                self.max_pages = num_of_pages
                
        except Exception as e:
            logging.error(f"Error: {e}")
            
    def print_news(self):
        for news in self.news_list:
            print(news["title"], news["date"])
            
    def get_news(self):
        if self.topic != '' or len(self.topic) > 2 :
            self.set_filter()
            
        sorted = self.sort_by_newest()
        self.get_max_pages()
        
        logging.info("Getting news...")
        logging.info(f"Max pages: {self.max_pages}")
        
        try:
            while self.page_count < self.max_pages:
                self.browser.wait_until_element_is_visible('css:ul.search-results-module-results-menu')
                self.load_news()
                ul_locator = 'css:ul.search-results-module-results-menu'
                li_elements = self.browser.get_webelements(ul_locator + ' > li')
                break_while = False
                
                for li in li_elements:
                    try:
                        title = self.find_element(li, "tag name", "h3")
                        description = self.find_element(li, "class name", "promo-description")
                        date = li.find_element("class name", "promo-timestamp").text
                        date = self.find_element(li, "class name", "promo-timestamp")
                        
                        if date == '':
                            continue
                        
                        date = utils.format_date(date)          
                        formatted_date = utils.format_date_to_month_year(date)
                        
                        if formatted_date not in self.period and sorted:
                            break_while = True
                            break
                        
                        if formatted_date not in self.period:
                            continue
                        
                        image_filename = self.find_image(li)
                        count_search_phrase = utils.count_search_phrase(self.search_phrase, title, description)
                        contains_money = utils.contains_money(title, description)
                        
                        self.news_list.append({'title': title, 'description': description, 
                                        'date': date, 'image_filename': image_filename,
                                        'count_search_phrase': count_search_phrase,
                                        'contains_money': contains_money},
                                        )
                    except Exception as e:
                        logging.error(f"Error: {e}")
                        
                
                
                if break_while:
                    break
                
                self.page_count += 1
                can_go_next = self.go_to_next_page()
                
                if not can_go_next:
                    logging.warning("Can't go to next page")
                    break
                
            self.print_news()
                
        except Exception as e:
            logging.error(f"Error: {e}")
            
    def download_image(self, url, image_filename):
        try:
            image_type = url.split('.')[-1]
            if image_type != 'jpeg' and image_type != 'jpg' and image_type != 'png' and image_type != 'gif' and image_type != 'webp':
                image_type = 'png'
            filename = "output/images/"+ uuid.uuid4().hex + '.' + image_type
            logging.info(f"Downloading image: {url}")
        
            response = requests.get(url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
            else:
                logging.warning(f"Can't download image: {url}")
        
            return filename
        except Exception as e:
            logging.error(f"Error: {e}")
            return ''
        
    def all_files(self):
        try:
            files = glob.glob('./output/images/*')
            wi = WorkItems()
            wi.get_input_work_item()
            wi.create_output_work_item(files=files, save=True)
        except Exception as e:
            logging.error(f"Error: {e}")
        
    def save_on_excel(self):
        try:
            headers = ['title', 'description', 'date', 'image_filename', 'count_search_phrase', 'contains_money', 'filename']
            rows = {header: [] for header in headers}
            
            if os.path.exists('./output/images') == False:
                logging.info("Creating output folder...")
                os.makedirs('./output/images')
            
            logging.info("Saving news on excel...")
            
            for news in self.news_list:
                for header in headers[:-1]:
                    if header in news.keys():
                        rows[header].append(news[header])
                        if header == 'image_filename' and news[header] != '':
                           filename = self.download_image(news[header], news['title'])
                           rows['filename'].append(filename)
                    
                    else:
                        rows[header].append('')
            
            self.all_files()
            self.excel.create_workbook(path="./output/news.xlsx")
            self.excel.create_worksheet("news")
            self.excel.append_rows_to_worksheet(rows, header=True)
            self.excel.save_workbook()
            self.excel.close_workbook()
                                                          
        except Exception as e:
            logging.error(f"Error on save_on_excel: {e}")