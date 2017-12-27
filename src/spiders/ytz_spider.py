from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem

class YTZSpider(AirportSpider):
    name = "ytz_spider"
    allowed_domains = ["tpaairport.78digital.com"]
    urls = [
        "https://tpaairport.78digital.com/dev/Departures.aspx",
        "https://tpaairport.78digital.com/dev/Arrivals.aspx"
    ]
    YTZ = "YTZ"
    LOGO = "logo-"
    MAIN = "MAIN"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YTZSpider.YTZ

    def start_requests(self):
        yield Request(url=YTZSpider.urls[0], callback=self.__departure_parse)

    def __departure_parse(self, response):
        flights = Selector(response).xpath("//table[@id='flights-listing']/tr[@class!='table-head']")
        departure_info = []
        for flight in flights:
            departure_info.append(self.__derive_flight(flight, AirportSpider.DEP))
        self.airport_flights["departures"] = departure_info
        yield Request(url=YTZSpider.urls[1], callback=self.__arrival_parse)
    
    def __arrival_parse(self, response):
        flights = Selector(response).xpath("//table[@id='flights-listing']/tr[@class!='table-head']")
        arrival_info = []
        for flight in flights:
            arrival_info.append(self.__derive_flight(flight, AirportSpider.ARR))
        self.airport_flights["arrivals"] = arrival_info
        yield self.airport_flights
    
    def __derive_flight(self, flight, leg):
        flight_data = flight.xpath("./td/text()").extract()
        flight_item = FlightItem()
        flight_item["leg"] = leg
        flight_item["airline"] = flight.xpath("./td/div/@class").extract_first()[len(YTZSpider.LOGO):]
        flight_item["flight_no"] = flight_data[2].strip()
        flight_item["city"] = flight_data[3].strip().upper()
        flight_item["expected_time"] = self.date + "T" + flight_data[4].strip() + AirportSpider.SECONDS_SUFFIX
        flight_item["actual_time"] = self.date + "T" + flight_data[5].strip() + AirportSpider.SECONDS_SUFFIX
        flight_item["status"] = flight_data[6].strip()
        flight_item["terminal"] = YTZSpider.MAIN
        flight_item["gate"] = AirportSpider.UNKNOWN
        return flight_item