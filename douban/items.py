# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field

class doubanItem(Item):
    # define the fields for your item here like:
    Name=Field()
    Email=Field()
    ProfileURL=Field()
    Country=Field()
    Organize=Field()
    PersonalURL=Field()
    Repositories=Field()
    Stars=Field()
    Followers=Field()
    Following=Field()
    Like=Field()