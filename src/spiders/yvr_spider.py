from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
from dateutil import parser
from datetime import datetime, timedelta
import json

class YVRSpider(AirportSpider):
    name = "yvr_spider"
    allowed_domains = ["www.yvr.ca"]
    start_urls = [
        "http://www.yvr.ca/en/_api/Flights"
    ]
    ICAO_CODE = "YVR"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YVRSpider.ICAO_CODE

    def parse(self, response):
        flights = json.loads(Selector(response).xpath("//p/text()").extract_first())
        for flight in flights["value"]:
            flight_date = flight["FlightEstimatedTime"][0:10]
            if flight_date == self.date:
                if flight["FlightType"] == AirportSpider.ARR:
                    self.airport_flights["arrivals"].append(self.__derive_flight(flight, AirportSpider.ARR))
                elif flight["FlightType"] == AirportSpider.DEP:
                    self.airport_flights["departures"].append(self.__derive_flight(flight, AirportSpider.DEP))
        yield self.airport_flights

    def __derive_flight(self, flight, leg):
        flight_item = FlightItem()
        flight_item["leg"] = leg
        flight_item["airline"] = flight["FlightAirlineName"]
        flight_item["flight_no"] = flight["FlightNumber"]
        flight_item["expected_time"] = flight["FlightScheduledTime"]
        flight_item["actual_time"] = flight["FlightEstimatedTime"]
        flight_item["status"] = flight["FlightStatus"]
        flight_item["terminal"] = AirportSpider.MAIN
        flight_item["gate"] = flight["FlightGate"]
        flight_item["city"] = flight["FlightCity"]

        return flight_item
