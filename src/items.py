# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AirportFlightItem(scrapy.Item):
    datetime_of_collection = scrapy.Field()
    airport = scrapy.Field()
    departures = scrapy.Field()
    arrivals = scrapy.Field()

class DepartureItem(scrapy.Item):
    airline = scrapy.Field()
    flight_no = scrapy.Field()
    destination = scrapy.Field()
    expected_departure = scrapy.Field()
    actual_departure = scrapy.Field()
    status = scrapy.Field()
    terminal = scrapy.Field()
    gate = scrapy.Field()

class ArrivalItem(scrapy.Item):
    airline = scrapy.Field()
    flight_no = scrapy.Field()
    origin = scrapy.Field()
    expected_arrival = scrapy.Field()
    actual_arrival = scrapy.Field()
    status = scrapy.Field()
    terminal = scrapy.Field()
    gate = scrapy.Field()

