# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IturingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    category = scrapy.Field()  # 分类
    book_name = scrapy.Field()  # 书名
    author = scrapy.Field()  # 作者
    price = scrapy.Field()  # 价格
    reading = scrapy.Field()  # 阅读量
    like = scrapy.Field()  # 加入心愿单
