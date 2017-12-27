from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
from ast import literal_eval

class YYZSpider(AirportSpider):
    name = "yyz_spider"
    allowed_domains = ["www.torontopearson.com"]
    urls = [
        "https://www.torontopearson.com/FlightScheduleData/dep_gtaa_data_today.txt",
        "https://www.torontopearson.com/FlightScheduleData/arr_gtaa_data_today.txt"
    ]
    YYZ = "YYZ"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YYZSpider.YYZ

    def start_requests(self):
        yield Request(url=YYZSpider.urls[0], callback=self.__departure_parse)

    def __departure_parse(self, response):
        flights = literal_eval(Selector(response).xpath("//p/text()").extract_first())["aaData"]
        departure_info = []
        for flight in flights:
            departure_info.append(self.__derive_flight(flight, AirportSpider.DEP))
        self.airport_flights["departures"] = departure_info
        yield Request(url=YYZSpider.urls[1], callback=self.__arrival_parse)
    
    def __arrival_parse(self, response):
        flights = literal_eval(Selector(response).xpath("//p/text()").extract_first())["aaData"]
        arrival_info = []
        for flight in flights:
            arrival_info.append(self.__derive_flight(flight, AirportSpider.ARR))
        self.airport_flights["arrivals"] = arrival_info
        yield self.airport_flights
    
    def __derive_flight(self, flight, leg):
        flight_item = FlightItem()
        flight_item["leg"] = leg
        flight_item["airline"] = flight[0].strip()
        flight_item["flight_no"] = flight[1].strip()
        flight_item["city"] = flight[2].strip()
        flight_item["expected_time"] = self.date + "T" + flight[3].strip().split()[2] + AirportSpider.SECONDS_SUFFIX
        flight_item["actual_time"] = self.date + "T" + flight[4].strip().split()[2] + AirportSpider.SECONDS_SUFFIX
        flight_item["status"] = flight[5].strip()
        flight_item["terminal"] = flight[6].strip()
        flight_item["gate"] = flight[9].strip()
        return flight_item
