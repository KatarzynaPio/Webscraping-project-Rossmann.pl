import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.crawler import CrawlerProcess
import time
from items import Rossmann

class CrawlSpider(CrawlSpider):
    name = 'products'
    allowed_domains = ['rossmann.pl']
    
    #It is manual at the moment, just to check if it goes over pages.
    numberOfProductsMax = 3
    start_urls = ["https://www.rossmann.pl/promocje?Page=%s" % page for page in range(1,numberOfProductsMax+1)]

#This is for the first page, and it only scrapes the first "old price". I couldn't manage to make a dictionary to have all details.
    #first_page = LinkExtractor(allow=r'/promocje')

    def parse_start_url(self, response):
        return self.parse_item(response)

#it finds every link that starts with /Produkt which is always 24
    #product_details = LinkExtractor(allow=r'Produkt/')
    
    first_page_rule = Rule(start_urls,  callback='parse_start_url', follow=False)
    #rule_product_details = Rule(product_details, callback='parse_item', follow=False)

    rules = (
        first_page_rule,
       # rule_product_details,
    )

    def parse_item(self,response):
        item = Rossmann()
       # item['Name'] = response.xpath('//h1[@class="h1"]/text()').extract(),
       # item['Size'] = response.xpath('//h2[@class="product-info__caption"]/text()[2]').get(),
       # item['Link'] = response.url,
       # Availability = response.xpath("//*[contains(text(), 'NIEDOSTĘPNY ONLINE')]").getall()
       # if len(Availability) > 1:
       #     Availability = "NIEDOSTĘPNY ONLINE"
       # else:
       #     Availability = "AVAILABLE ONLINE"
       # item['Availability'] = Availability
        
        #-----------------------------
        item['price_regular'] = response.xpath('//*[@class = "tile-product__old-price"]').getall(),
        print("TEST--regular price-------------")
        print(item['price_regular'])
        item['price_promo'] = response.xpath('//*[@class = "tile-product__promo-price"]').getall(),
        print("TEST--promo price-------------")
        print(item['price_promo'])
        #-----------------------------

        
        #this does not work
        #item['rate'] = response.xpath('//span[@class="stars mr-2"]').get()
        
        # it works 
        #item['numberOfReviews'] = ''.join(response.xpath('//*[@class = "product-info__rate d-flex py-2"]/span/text()').getall())

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
