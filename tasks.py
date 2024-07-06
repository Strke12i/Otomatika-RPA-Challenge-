from robocorp import browser
from robocorp.tasks import task
from config import Config
from scrapper import Scrapper
import logging


@task
def solve_challenge():
    config = Config()
    scrapper = Scrapper(config.url, config.topic, 
                        config.search_phrase,
                        config.get_period())
    
    scrapper.open_browser()
    scrapper.search_news()    
    scrapper.get_news()
    scrapper.save_on_excel()
    
