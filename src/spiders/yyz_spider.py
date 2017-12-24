from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import DepartureItem, ArrivalItem
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
            departure_item = DepartureItem()
            departure_item["airline"] = flight[0].strip()
            departure_item["flight_no"] = flight[1].strip()
            departure_item["destination"] = flight[2].strip()
            departure_item["expected_departure"] = flight[3].strip()
            departure_item["actual_departure"] = flight[4].strip()
            departure_item["status"] = flight[5].strip()
            departure_item["terminal"] = flight[6].strip()
            departure_item["gate"] = flight[9].strip()
            departure_info.append(departure_item)
        self.airport_flights["departures"] = departure_info
        yield Request(url=YYZSpider.urls[1], callback=self.__arrival_parse)
    
    def __arrival_parse(self, response):
        flights = literal_eval(Selector(response).xpath("//p/text()").extract_first())["aaData"]
        arrival_info = []
        for flight in flights:
            arrival_item = ArrivalItem()
            arrival_item["airline"] = flight[0].strip()
            arrival_item["flight_no"] = flight[1].strip()
            arrival_item["origin"] = flight[2].strip()
            arrival_item["expected_arrival"] = flight[3].strip()
            arrival_item["actual_arrival"] = flight[4].strip()
            arrival_item["status"] = flight[5].strip()
            arrival_item["terminal"] = flight[6].strip()
            arrival_item["gate"] = flight[9].strip()
            arrival_info.append(arrival_item)
        self.airport_flights["arrivals"] = arrival_info
        yield self.airport_flights