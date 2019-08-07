# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewHouseItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    # 幾居,是列表
    rooms = scrapy.Field()
    area = scrapy.Field()
    address = scrapy.Field()
    district = scrapy.Field()
    sale = scrapy.Field()
    origin_url = scrapy.Field()


class ESFHouseItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    name = scrapy.Field()
    # 幾窒幾廳
    rooms = scrapy.Field()
    # 層
    floor = scrapy.Field()
    # 朝向
    toward = scrapy.Field()
    # 年代
    year = scrapy.Field()
    address = scrapy.Field()
    area = scrapy.Field()
    # 總價
    price = scrapy.Field()
    # 單價
    unit = scrapy.Field()
    origin_url = scrapy.Field()
