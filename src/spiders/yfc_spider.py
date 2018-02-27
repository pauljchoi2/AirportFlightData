from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
import datetime

class YFCSpider(AirportSpider):
    name = "yfc_spider"
    allowed_domains = ["frederictonairport.ca"]
    start_urls = [
        "https://www.frederictonairport.ca/arrivals-departures/"
    ]
    ICAO_CODE = "YFC"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YFCSpider.ICAO_CODE
        self.date = datetime.datetime.now().date().strftime("%Y-%m-%d")

    def parse(self, response):
        departures = Selector(response).xpath("//div[@id='tabs-2']/table/tr[@class='arrivals']")
        arrivals = Selector(response).xpath("//div[@id='tabs-1']/table/tr[@class='arrivals']")
        for departure in departures:
            self.airport_flights["departures"].append(self.__derive_flight(departure, AirportSpider.DEP))
        for arrival in arrivals:
            self.airport_flights["arrivals"].append(self.__derive_flight(arrival, AirportSpider.ARR))
      
        yield self.airport_flights

    def __derive_flight(self, flight, leg):
        flight_item = FlightItem()
        flight_item["leg"] = leg
        flight_info = flight.xpath("./td/text()").extract()
        flight_item["airline"] = flight_info[0]
        flight_item["flight_no"] = flight_info[1]
        flight_item["city"] = flight_info[2]
        flight_item["expected_time"] = self.date + "T" + flight_info[3] + AirportSpider.SECONDS_SUFFIX
        flight_item["actual_time"] = self.date + "T" + flight_info[4] + AirportSpider.SECONDS_SUFFIX
        flight_item["status"] = flight_info[5]
        flight_item["gate"] = AirportSpider.UNKNOWN
        flight_item["terminal"] = AirportSpider.MAIN
        return flight_item