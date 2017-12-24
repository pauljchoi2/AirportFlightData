from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import DepartureItem, ArrivalItem

class YTZSpider(AirportSpider):
    name = "ytz_spider"
    allowed_domains = ["tpaairport.78digital.com"]
    urls = [
        "https://tpaairport.78digital.com/dev/Departures.aspx",
        "https://tpaairport.78digital.com/dev/Arrivals.aspx"
    ]
    YTZ = "YTZ"
    LOGO = "logo-"

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YTZSpider.YTZ

    def start_requests(self):
        yield Request(url=YTZSpider.urls[0], callback=self.__departure_parse)

    def __departure_parse(self, response):
        flights = Selector(response).xpath("//table[@id='flights-listing']/tr[@class!='table-head']")
        departure_info = []
        for flight in flights:
            departure_item = DepartureItem()
            departure_item["airline"] = flight.xpath("./td/div/@class").extract_first()[len(YTZSpider.LOGO):]
            flight_data = flight.xpath("./td/text()").extract()
            departure_item["flight_no"] = flight_data[2].strip()
            departure_item["destination"] = flight_data[3].strip().upper()
            departure_item["expected_departure"] = flight_data[4].strip()
            departure_item["actual_departure"] = flight_data[5].strip()
            departure_item["status"] = flight_data[6].strip()
            departure_info.append(departure_item)
        self.airport_flights["departures"] = departure_info
        yield Request(url=YTZSpider.urls[1], callback=self.__arrival_parse)
    
    def __arrival_parse(self, response):
        flights = Selector(response).xpath("//table[@id='flights-listing']/tr[@class!='table-head']")
        arrival_info = []
        for flight in flights:
            arrival_item = ArrivalItem()
            arrival_item["airline"] = flight.xpath("./td/div/@class").extract_first()[len(YTZSpider.LOGO):]
            flight_data = flight.xpath("./td/text()").extract()
            arrival_item["flight_no"] = flight_data[2].strip()
            arrival_item["origin"] = flight_data[3].strip().upper()
            arrival_item["expected_arrival"] = flight_data[4].strip()
            arrival_item["actual_arrival"] = flight_data[5].strip()
            arrival_item["status"] = flight_data[6].strip()
            arrival_info.append(arrival_item)
        self.airport_flights["arrivals"] = arrival_info
        yield self.airport_flights