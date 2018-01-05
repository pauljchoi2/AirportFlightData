from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
from datetime import datetime
import json

class YYJSpider(AirportSpider):
    name = "yyj_spider"
    allowed_domains = ["www.victoriaairport.com"]
    start_urls = [
        "http://www.victoriaairport.com/arrivals",
        "http://www.victoriaairport.com/departures"
    ]
    ICAO_CODE = "YYJ"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YYJSpider.ICAO_CODE

    def parse(self, response):
        flights = Selector(response).xpath("//div[@id='flightinfo']/table/tbody")[0]
        flights = flights.xpath("./tr")[1:]
        process_departures = AirportSpider.DEPARTURES.lower() in response.url.split("/")
        process_arrivals = AirportSpider.ARRIVALS.lower() in response.url.split("/")
        for flight in flights:
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
        flight_item["airline"] = flight.xpath("./td/img/@alt").extract_first()
        flight_item["flight_no"] = flight.xpath("./td[@class='flight']/text()").extract_first()
        flight_actual_time = flight.xpath("./td[@style='line-height: normal;']/text()").extract()[1]
        flight_item["expected_time"] = self.date + datetime.strftime(datetime.strptime(flight_actual_time.strip(), "%I:%M %p"), "T%H:%M:%SZ")
        flight_status_time = flight.xpath("./td/em/text()").extract()
        if flight_status_time is None:
            flight_item["actual_time"] = flight_item["expected_time"]
        else:
            if len(flight_status_time) == 0:
                flight_item["actual_time"] = flight_item["expected_time"]
            else:
                flight_item["actual_time"] = self.date + datetime.strftime(datetime.strptime(flight_status_time[1].strip(), "%I:%M %p"), "T%H:%M:%SZ")
        flight_item["status"] = flight.xpath("./td/em/text()").extract_first().strip() if flight.xpath("./td/em/text()").extract_first() is not None \
        else flight.xpath("./td[@class='status']/text()").extract_first()
        flight_item["terminal"] = AirportSpider.MAIN
        flight_item["gate"] = flight.xpath("./td[@style='text-align: center;']/text()").extract_first()
        flight_item["city"] = flight.xpath("./td[@class='city']/text()").extract_first()

        return flight_item
