from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
from dateutil import parser
from datetime import datetime, timedelta

class YQBSpider(AirportSpider):
    name = "yqb_spider"
    allowed_domains = ["www.aeroportdequebec.com/en"]
    start_urls = [
        "https://www.aeroportdequebec.com/en/flights-and-destinations/flight-schedules/departures",
        "https://www.aeroportdequebec.com/en/flights-and-destinations/flight-schedules/arrivals"
    ]
    ICAO_CODE = "YQB"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YQBSpider.ICAO_CODE

    def parse(self, response):
        flights = Selector(response).xpath("//table/tbody/tr")
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
        times = flight.xpath("./td/time/@datetime").extract()
        flight_item["leg"] = leg
        flight_item["airline"] = flight.xpath("./td/img/@alt").extract_first().strip()
        flight_item["flight_no"] = flight.xpath("./td/span[@class='visible-xs-inline']/text()").extract_first() + \
        flight.xpath("./td[@class='views-field views-field-field-flight-number']/text()").extract()[5].strip()
        flight_item["expected_time"] = datetime.strftime(datetime.strptime(times[0], "%Y-%m-%dT%XZ") - timedelta(hours=5), "%Y-%m-%dT%XZ")
        if len(times) == 2:
             flight_item["actual_time"] = datetime.strftime(datetime.strptime(times[1], "%Y-%m-%dT%XZ") - timedelta(hours=5), "%Y-%m-%dT%XZ")
        else:
            flight_item["actual_time"] = datetime.strftime(datetime.strptime(times[0], "%Y-%m-%dT%XZ") - timedelta(hours=5), "%Y-%m-%dT%XZ")
        flight_item["status"] = flight.xpath("./td[@class='views-field views-field-field-status']/text()").extract()[3].strip()
        flight_item["terminal"] = AirportSpider.MAIN
        gate_info = flight.xpath("./td[@class='views-field views-field-field-gate']/text()").extract()
        if len(gate_info) < 4:
            flight_item["gate"] = AirportSpider.UNKNOWN
        else:
            flight_item["gate"] = gate_info[3].strip()
        flight_item["city"] = flight.xpath("./td/div/div/div/div/div/text()").extract()[3].strip()

        return flight_item
