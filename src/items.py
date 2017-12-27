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

class FlightItem(scrapy.Item):
    airline = scrapy.Field()
    flight_no = scrapy.Field()
    leg = scrapy.Field()
    city = scrapy.Field()
    expected_time = scrapy.Field()
    actual_time = scrapy.Field()
    status = scrapy.Field()
    terminal = scrapy.Field()
    gate = scrapy.Field()
