from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
import datetime

class YYGSpider(AirportSpider):
    name = "yyg_spider"
    allowed_domains = ["flypei.com"]
    start_urls = [
        "http://flypei.com/fids/arriv_dep_full_info.php?type=departures",
        "http://flypei.com/fids/arriv_dep_full_info.php?type=arrivals"
    ]
    ICAO_CODE = "YYG"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YYGSpider.ICAO_CODE
        self.date = datetime.datetime.now().date().strftime("%Y-%m-%d")

    def parse(self, response):
        flights = Selector(response).xpath("//table[@class='flightinfo']/tr")
        process_departures = AirportSpider.DEPARTURES.lower() in response.url
        process_arrivals = AirportSpider.ARRIVALS.lower() in response.url
        for flight in flights[1:-1]:
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
        flight_info = flight.xpath("./td/text()").extract()
        flight_item["airline"] = flight_info[0]
        flight_item["flight_no"] = flight_info[1]
        flight_item["city"] = flight_info[4]
        flight_item["expected_time"] = self.date + "T" + flight_info[2] + AirportSpider.SECONDS_SUFFIX
        flight_item["actual_time"] = self.date + "T" + flight_info[3] + AirportSpider.SECONDS_SUFFIX
        flight_item["status"] = flight_info[5]
        flight_item["gate"] = AirportSpider.UNKNOWN
        flight_item["terminal"] = AirportSpider.MAIN
        return flight_item