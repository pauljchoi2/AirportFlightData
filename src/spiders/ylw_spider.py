from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
from datetime import datetime, timedelta

class YLWSpider(AirportSpider):
    name = "ylw_spider"
    allowed_domains = ["ylw.kelowna.ca"]
    start_urls = [
        "https://ylw.kelowna.ca/sites/files/3/xml/departures.xml",
        "https://ylw.kelowna.ca/sites/files/3/xml/arrivals.xml"
    ]
    ICAO_CODE = "YLW"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YLWSpider.ICAO_CODE

    def parse(self, response):
        flights = Selector(response).xpath("//data/Record")
        process_departures = AirportSpider.DEPARTURES.lower() in response.url
        process_arrivals = AirportSpider.ARRIVALS.lower() in response.url
        for flight in flights:
            if process_arrivals:
                self.airport_flights["arrivals"].append(self.__derive_flight(flight, AirportSpider.ARR))
            elif process_departures:
                self.airport_flights["departures"].append(self.__derive_flight(flight, AirportSpider.DEP))
        if process_arrivals:
            self.arrivals_processed = True
        elif process_departures:
            self.departures_processed = True
        print(self.arrivals_processed)
        print(self.departures_processed)
        if self.departures_processed and self.arrivals_processed:
            yield self.airport_flights

    def __derive_flight(self, flight, leg):
        flight_item = FlightItem()
        flight_item["leg"] = leg
        flight_item["airline"] = flight.xpath("./AirlineCode/text()").extract_first()
        flight_item["flight_no"] = flight_item["airline"] + flight.xpath("./FlightNumber/text()").extract_first()
        flight_item["expected_time"] = datetime.strftime(datetime.strptime(flight.xpath("./FlightDate/text()").extract_first(), "%Y%m%d"), "%Y-%m-%d") + \
        datetime.strftime(datetime.strptime(flight.xpath("./ScheduleTime/text()").extract_first(), "%H%M"), "T%H:%M") + AirportSpider.SECONDS_SUFFIX
        flight_item["actual_time"] = datetime.strftime(datetime.strptime(flight.xpath("./EstimatedTime/text()").extract_first(), "%Y%m%d%H%M"), "%Y-%m-%dT%H:%M:00Z")
        flight_item["status"] = flight.xpath("./Status/text()").extract_first()
        flight_item["gate"] = flight.xpath("./Gate/text()").extract_first()
        flight_item["city"] = flight.xpath("./ViaAirportCity/text()").extract_first()
        flight_item["terminal"] = AirportSpider.MAIN

        return flight_item
