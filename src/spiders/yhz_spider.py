from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
from dateutil import parser
import datetime
import json

class YHZSpider(AirportSpider):
    name = "yhz_spider"
    allowed_domains = ["halifaxstanfield.ca"]
    start_urls = [
        "https://halifaxstanfield.ca/flight-information/arrivals/",
        "https://halifaxstanfield.ca/flight-information/departures/"
    ]
    ICAO_CODE = "YHZ"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YHZSpider.ICAO_CODE
        self.date = datetime.datetime.now().date().strftime("%Y-%m-%d")

    def parse(self, response):
        flight_type = response.url.split("/")[4]
        flights = Selector(response).xpath("//div[@id='" + flight_type + "']/ul/li")
        process_departures = AirportSpider.DEPARTURES.lower()[:-1] in response.url
        process_arrivals = AirportSpider.ARRIVALS.lower()[:-1] in response.url
        for flight in flights[1:]:
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
        flight_item["airline"] = flight.xpath("./ul/li[@class='carrier']/a/span/span/text()").extract_first()
        airline_code = flight.xpath("./ul/li[@class='carrier']/a/span/i/@data-code").extract_first()
        flight_no = flight.xpath("./ul/li[@class='number']/span/text()").extract_first()
        flight_item["flight_no"] = airline_code + flight_no
        flight_item["city"] = flight.xpath("./ul/li[@class='location']/span/text()").extract_first()
        expected_time = flight.xpath("./ul/li[@class='expected-time']/span/text()").extract_first()
        flight_item["expected_time"] = self.date + "T" + expected_time + AirportSpider.SECONDS_SUFFIX
        actual_time = flight.xpath("./ul/li[@class='actual-time']/span/text()").extract_first()
        flight_item["actual_time"] = self.date + "T" + actual_time + AirportSpider.SECONDS_SUFFIX
        flight_item["status"] = flight.xpath("./ul/li[@class='status']/span/text()").extract_first()
        flight_item["gate"] = flight.xpath("./ul/li[@class='gate']/span/text()").extract_first()
        flight_item["terminal"] = AirportSpider.MAIN
        return flight_item