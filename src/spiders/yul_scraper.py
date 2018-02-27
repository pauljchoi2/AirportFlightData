from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
from dateutil import parser
import datetime
import json

class YULSpider(AirportSpider):
    name = "yul_spider"
    allowed_domains = ["http://www.admtl.com/en"]
    start_urls = [
        "https://www.admtl.com/en/admtldata/api/flight?type=departure&rule=24h",
        "http://www.admtl.com/en/admtldata/api/flight?type=arrival&rule=24h"
    ]
    ICAO_CODE = "YUL"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YULSpider.ICAO_CODE

    def parse(self, response):
        flights = json.loads(Selector(response).xpath("//p/text()").extract_first())
        process_departures = AirportSpider.DEPARTURES.lower()[:-1] in response.url
        process_arrivals = AirportSpider.ARRIVALS.lower()[:-1] in response.url
        for flight in flights["data"]:
            if process_arrivals:
                self.airport_flights["arrivals"].append(self.__derive_flight(flight, AirportSpider.ARR))
            elif process_departures:
                self.airport_flights["departures"].append(self.__derive_flight(flight, AirportSpider.DEP))
        if process_arrivals:
            self.arrivals_processed = True
        elif process_departures:
            self.departures_processed = True
        if self.departures_processed and self.arrivals_processed:
            yield self.airport_flights

    def __derive_flight(self, flight, leg):
        flight_item = FlightItem()
        flight_item["leg"] = leg
        flight_item["airline"] = flight["company"]
        flight_item["flight_no"] = flight["flight"]
        flight_item["expected_time"] = self.date + "T" + flight["planned_hour"] + AirportSpider.SECONDS_SUFFIX
        if type(flight["revised_date"]) is str and type(flight["revised_hour"]) is str:
            flight_item["actual_time"] = parser.parse(flight["revised_date"]).strftime("%Y%m%d") + "T" + flight["revised_hour"] + AirportSpider.SECONDS_SUFFIX
        else:
            flight["actual_time"] = self.date
        flight_item["status"] = flight["details"]["status"]
        flight_item["terminal"] = AirportSpider.UNKNOWN
        flight_item["gate"] = flight["terminal_gate"]
        flight_item["city"] = flight["destination_without_accent"]

        return flight_item
