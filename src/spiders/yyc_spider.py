from scrapy import Selector, Request
from .airport_spider import AirportSpider
from src.items import FlightItem
import json
import datetime

class YYCSpider(AirportSpider):
    name = "yyc_spider"
    allowed_domains = ["flightdata.yyc.com"]
    start_urls = ["http://flightdata.yyc.com/api/flights"]
    ICAO_CODE = "YYC"
    DEP = "D"
    DOMESTIC_CONCOURSES = {"A", "B", "C"}
    INTERNATIONAL_CONCOURSES = {"D", "E"}

    def __init__(self):
        super().__init__()
        self.airport_flights["airport"] = YYCSpider.ICAO_CODE
        self.date = datetime.datetime.now().date().strftime("%Y%m%d")

    def parse(self, response):
        data_block = json.loads(Selector(response).xpath("//p/text()").extract_first())
        for flight in data_block["flights"]:    
            if flight["Id"][:8] == self.date:
                if flight["Leg"] == YYCSpider.DEP:
                    self.airport_flights["departures"].append(self.__derive_flight(flight, AirportSpider.DEP))
                else:
                    self.airport_flights["arrivals"].append(self.__derive_flight(flight, AirportSpider.ARR))
        yield self.airport_flights

    def __derive_flight(self, flight, leg):
        flight_item = FlightItem()
        gate = flight["Gate"]["Code"]
        flight_item["leg"] = leg
        flight_item["airline"] = flight["Airline"]["Name"]
        flight_item["flight_no"] = flight["Airline"]["Code"] + flight["FlightNumber"]
        flight_item["city"] = flight["Airport"]["Name"]
        flight_item["expected_time"] = flight["ScheduledTime"]
        flight_item["actual_time"] = flight["ActualTime"]
        flight_item["status"] = flight["YycStatus"]["PrimaryStatus"]["ShortEnglishText"]
        flight_item["gate"] = gate
        if (len(gate) > 1):
            if gate[0] in YYCSpider.DOMESTIC_CONCOURSES:
                flight_item["terminal"] = AirportSpider.DOMESTIC
            elif gate[0] in YYCSpider.INTERNATIONAL_CONCOURSES:
                flight_item["terminal"] = AirportSpider.INTERNATIONAL
            else:
                flight_item["terminal"] = AirportSpider.UNKNOWN
        else:
            flight_item["terminal"] = AirportSpider.UNKNOWN
        return flight_item
                
        
