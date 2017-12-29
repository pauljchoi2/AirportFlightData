from scrapy import Spider
from src.items import AirportFlightItem
import datetime

class AirportSpider(Spider):
    DEP = "D"
    ARR = "A"
    SECONDS_SUFFIX = ":00Z"
    DOMESTIC = "DOMESTIC"
    INTERNATIONAL = "INTERNATIONAL"
    UNKNOWN = "UNKNOWN"
    DEPARTURES = "DEPARTURES"
    ARRIVALS = "ARRIVALS"
    MAIN = "MAIN"

    def __init__(self):
        self.date = datetime.datetime.now().date().strftime("%Y-%m-%d")
        self.airport_flights = AirportFlightItem()
        self.airport_flights["datetime_of_collection"] = datetime.datetime.now().replace(microsecond=0).isoformat() + "Z"
        self.airport_flights["departures"] = []
        self.airport_flights["arrivals"] = []
        self.departures_processed = False
        self.arrivals_processed = False

    def __derive_flight(self, flight, leg):
        pass