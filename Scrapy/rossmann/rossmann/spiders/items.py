# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
class Rossmann(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Name = Field()
    Size = Field()
    Link = Field()
    Availability = Field()
    rate = Field()     
    numberOfReviews = Field()
    pass
