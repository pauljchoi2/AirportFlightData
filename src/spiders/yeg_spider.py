from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
from ast import literal_eval
from urllib.parse import urljoin

class YEGSpider(AirportSpider):
    name = "yeg_spider"
    allowed_domains = ["flyeia.com"]
    start_urls = ["http://flyeia.com/flights/departures", "http://flyeia.com/flights/arrivals"]
    YEG = "YEG"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YEGSpider.YEG
        self.airport_flights["departures"] = []
        self.airport_flights["arrivals"] = []
        self.departures_processed = False
        self.arrivals_processed = False

    def parse(self, response):
        flights = Selector(response).xpath("//tr[@class='odd'] | //tr[@class='even']")
        if response.url.split("/")[4] == AirportSpider.DEPARTURES.lower():
            self.airport_flights["departures"].append(self.__process_flights(flights, AirportSpider.DEP))
        else:
            self.airport_flights["arrivals"].append(self.__process_flights(flights, AirportSpider.ARR))
        
        pagination = Selector(response).xpath("//ul[@class='pager']/li")
        go_to_next_page = False
        for page in pagination:
            if go_to_next_page:
                return Request(url=urljoin("http://flyeia.com", page.xpath("./a/@href").extract_first()), callback=self.parse)
            if page.xpath("./@class").extract_first() == "pager-current first" or page.xpath("./@class").extract_first() == "pager-current":
                go_to_next_page = True
        if AirportSpider.DEPARTURES.lower() in response.url.split("/")[4]:
            self.departures_processed = True
        elif AirportSpider.ARRIVALS.lower() in response.url.split("/")[4]: 
            self.arrivals_processed = True
        if self.departures_processed and self.arrivals_processed:
            return self.airport_flights

    def __process_flights(self, flights, leg):
        flights_on_current_page = []
        for flight in flights:
            flights_on_current_page.append(self.__derive_flight(flight, leg))
        return flights_on_current_page
        
    def __derive_flight(self, flight, leg):
        flight_item = FlightItem()
        flight_info = flight.xpath("./td/text()").extract()
        flight_item["leg"] = leg
        flight_item["airline"] = flight_info[1]
        flight_item["flight_no"] = flight_info[0]
        flight_item["city"] = flight_info[2]
        flight_item["expected_time"] = flight_info[3]
        flight_item["actual_time"] = flight_info[4]
        flight_item["status"] = flight.xpath("./td/span/text()").extract_first()
        flight_item["gate"] = AirportSpider.UNKNOWN
        return flight_item