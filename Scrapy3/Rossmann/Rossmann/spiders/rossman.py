# -*- coding: utf-8 -*-
import scrapy
from scrapy.item import Field

class Rossmann(scrapy.Item):
    # define the fields for your item here like:
    #name = scrapy.Field()
    Name = Field()
    Size = Field()
    Link = Field()
    Availability = Field()
    Rate = Field()     
    NumberOfReviews = Field()
    NewPrice = Field()
    OldPrice = Field()
    Category = Field()


class SpiderSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = ['https://www.rossmann.pl']
    base_url = 'https://www.rossmann.pl'

    def start_requests(self):
        numberOfProductsMax = 2
        urls = ["https://www.rossmann.pl/promocje?Page=%s" % page for page in range(1,numberOfProductsMax+1)]
        for url in urls:
            yield scrapy.Request(url, self.parse, dont_filter=True)

    def parse(self, response):
        all_products = response.xpath('//div[@class="tile-product"]')
        all_prices_promo = response.xpath('//span[@class="tile-product__promo-price"]/text()').extract()
        all_prices_regular = response.xpath('//span[@class="tile-product__old-price"]/text()').extract()
        for i in range(len(all_products)):
            product_url = all_products[i].xpath('a/@href').extract_first()
            prices = {'regular': all_prices_regular[i],'promo':all_prices_promo[i]}
            if 'Produkt/' not in product_url:
                product_url = 'Produkt/' + product_url
            product_url = self.base_url + product_url
            yield scrapy.Request(product_url, callback=self.parse_product, dont_filter=True, meta={'item': prices})

    def parse_product(self, response):
        initial_info = response.meta['item']
        item = Rossmann() 
        item['NewPrice'] = initial_info['promo']
        item['OldPrice'] = initial_info['regular']
        item['Name'] = response.xpath('//h1[@class="h1"]/text()').extract(),
        item['Size'] = response.xpath('//h2[@class="product-info__caption"]/text()[2]').get(),
        item['Category'] = '/'.join(response.xpath('//li[@class="breadcrumb-item"]/a/span/text()').getall()[1:]),
        item['Link'] = response.url,
        Availability = response.xpath("//*[contains(text(), 'NIEDOSTĘPNY ONLINE')]").getall()
        if len(Availability) > 1:
            Availability = "NIEDOSTĘPNY ONLINE"
        else:
            Availability = "AVAILABLE ONLINE"
        item['Availability'] = Availability
        NumberOfReviews = response.xpath('//*[@class = "product-info__rate d-flex py-2"]/span/text()[2]').extract()
        if NumberOfReviews:
            item['NumberOfReviews'] = NumberOfReviews[0]
        else:
            item['NumberOfReviews'] = "None"
        Rate = response.xpath('//@data-rate').extract_first()
        if Rate:
            item['Rate'] = Rate[0]
        else:
            item['Rate'] = "None"
        
        yield item


