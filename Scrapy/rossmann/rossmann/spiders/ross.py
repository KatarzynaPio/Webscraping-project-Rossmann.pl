import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class BooksCrawlSpider(CrawlSpider):
    name = 'products_crawl'
    allowed_domains = ['rossmann.pl']
    
    #It is manual at the moment, just to check if it goes over pages.
    num_pages = 3
    def start_requests(self):
        requests = []
        for i in range(1, self.num_pages):
            requests.append(scrapy.Request(
                url='https://www.rossmann.pl/promocje?Page={0}'.format(i)
            ))
        return requests

#This is for the first page, and it only scrapes the first "old price". I couldn't manage to make a dictionary to have all details.
    first_page = LinkExtractor(allow=r'/promocje')

    def parse_start_url(self, response):
        return self.parse_item(response)

#it finds every link that starts with /Produkt which is always 24
    product_details = LinkExtractor(allow=r'Produkt/')

    first_page_rule = Rule(first_page,  callback='parse_start_url', follow=False)
    rule_product_details = Rule(product_details, callback='parse_item', follow=False)

    rules = (
        first_page_rule,
        rule_product_details,
    )

    def parse_item(self, response):
        yield {
            'Title': response.xpath('//h1[@class="h1"]/text()').extract(),
            'Price': response.xpath('//span[@class="tile-product__old-price"]/text()').get(),
            'Description': response.xpath('//div[@class="my-2 my-lg-3"]/h2/text()').get(),
            'Size': response.xpath('//h2[@class="product-info__caption"]/text()[2]').get(),
            'Link': response.url,
        }
