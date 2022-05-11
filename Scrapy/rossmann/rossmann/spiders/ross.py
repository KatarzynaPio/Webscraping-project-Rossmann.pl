import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
import time
from items import Rossmann
from scrapy import Request


class CrawlSpider(CrawlSpider):
    name = 'products'
    allowed_domains = ['rossmann.pl']
    
    numberOfProductsMax = 8
    start_urls = ["https://www.rossmann.pl/promocje?Page=%s" % page for page in range(1,numberOfProductsMax+1)]

    product_details = LinkExtractor(allow=r'Produkt/')
    first_page_rule = Rule(start_urls, callback='parse_start_url', follow=False)
    rule_product_details = Rule(product_details, callback='parse_item', follow=False)
    rules = (
        rule_product_details,
        first_page_rule
    )

    def parse_item(self,response):
        item = Rossmann()
        item['Name'] = response.xpath('//h1[@class="h1"]/text()').extract(),
        item['Size'] = response.xpath('//h2[@class="product-info__caption"]/text()[2]').get(),
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
    

    def parse_start_url(self, response):
        item = Rossmann()
        new_prices = response.xpath('//span[@class="tile-product__promo-price"]/text()').extract()
        old_sellers = response.xpath('//span[@class="tile-product__old-price"]/text()').extract()
        for price, seller in zip(new_prices, old_sellers):
            item['NewPrice'] = price.strip()
            item['OldPrice'] = seller.strip()
            yield item

process = CrawlerProcess(settings={
    "FEEDS": {
        "items.csv": {"format": "csv"},
    },  
})

#It is automated now
#Running the spider
process.crawl(CrawlSpider)
process.start()
