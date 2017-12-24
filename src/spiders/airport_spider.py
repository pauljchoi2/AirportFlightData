from scrapy import Spider
from src.items import AirportFlightItem, DepartureItem, ArrivalItem
import datetime

class AirportSpider(Spider):

    def __init__(self):
        self.airport_flights = AirportFlightItem()
        self.airport_flights["datetime_of_collection"] = datetime.datetime.now()