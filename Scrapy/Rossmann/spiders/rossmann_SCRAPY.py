import time
import scrapy
from scrapy.item import Field
import math



################
## CONSTANTS  ##
################
MAIN_ULR = 'https://www.rossmann.pl'
PROMOCJE_TAB = 'https://www.rossmann.pl/promocje?Page=%s'
NUM_OF_PROD_MAX = 3000 # the maximum number of products for which the program should scrape data


####################
### MAIN PROGRAM ###
####################
class Rossmann(scrapy.Item):
    Name = Field()
    #Size = Field()
    Link = Field()
    Availability = Field()
    Description = Field()
    Image = Field()
    Rate = Field()     
    NumberOfReviews = Field()
    PromoPrice = Field()
    RegularPrice = Field()
    Categories = Field()
    Gender = Field()


class SpiderSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = [MAIN_ULR]
    base_url = MAIN_ULR
    Products_scraped = 0

    def start_requests(self):
        numberOfProductsMax = NUM_OF_PROD_MAX
        NumberOfPages = math.ceil(numberOfProductsMax/24)
        
        # create the list with all urls which need to be scraped
        # get these pages by changing last part of the url for the 'Promocje' tab
        urls = [PROMOCJE_TAB % page for page in range(1,NumberOfPages+1)]

        # loop through the urls list and sent request to each of the url
        # sent request len(ulr) times to scrape information about NUM_OF_PROD_MAX products
        # add dont_filter=True, to do not filter out the duplicate requests
        for url in urls:
            yield scrapy.Request(url, self.parse, dont_filter=True)

    def parse(self, response):

        # scrape basic information about products from one of the page in Promocje tab
        # basic information -> regular price, promotion price and link to page for the given product
        all_products = response.xpath('//div[@class="tile-product"]')
        all_prices_promo = response.xpath('//span[@class="tile-product__promo-price"]/text()').extract()
        all_prices_regular = response.xpath('//span[@class="tile-product__old-price"]/text()').extract()

        # loop through all products on given page in Promocje tab
        # and go to product page
        for i in range(len(all_products)):
            if self.Products_scraped > NUM_OF_PROD_MAX:
                break
            product_url = all_products[i].xpath('a/@href').extract_first()
            prices = {'regular': all_prices_regular[i],'promo':all_prices_promo[i]}
            if 'Produkt/' not in product_url:
                product_url = 'Produkt/' + product_url
            product_url = self.base_url + product_url
            # go to page for given product, 
            # use meta={'item': prices} argument to provide information about prices to parse_product()
            # these two pieces of information need to be scraped from the
            # Promocje tab and provided to the next step because scrapy is unable to get the prices from the product page
            yield scrapy.Request(product_url, callback=self.parse_product, dont_filter=True, meta={'item': prices})

    def parse_product(self, response):
        
        self.Products_scraped += 1
        initial_info = response.meta['item']
        item = Rossmann() 

        # Scrape detial information about product
        item['PromoPrice'] = initial_info['promo'].replace(',', '.').replace('zł','').strip()
        item['RegularPrice'] = initial_info['regular'].replace(',', '.').replace('zł','').strip()
        item['Name'] = ''.join(response.xpath('//h1[@class="h1"]/text()').extract())
        Description = response.xpath('//h2[@class="product-info__caption"]//text()').getall()
        item['Description'] = "".join(Description)
        
        Img = response.xpath('//div[@class="product-img"]/img/@src').get()
        if Img:
            item['Image'] = 'https:' + Img 
        else:
            item['Image'] = 'None'
        
        #item['Size'] = response.xpath('//h2[@class="product-info__caption"]/text()[2]').,
        item['Categories'] = '/'.join(response.xpath('//li[@class="breadcrumb-item"]/a/span/text()').getall()[1:])
        item['Link'] = response.url
        Availability = response.xpath("//*[contains(text(), 'NIEDOSTĘPNY ONLINE')]").getall()
        if len(Availability) > 1:
            Availability = "Unavailable online"
        else:
            Availability = "Available online"
        item['Availability'] = Availability
        
        NumberOfReviews = response.xpath('//*[@class = "product-info__rate d-flex py-2"]/span/text()').extract()            
        if NumberOfReviews:
            item['NumberOfReviews'] = NumberOfReviews[1]
        else:
            item['NumberOfReviews'] = "None"
        Rate = response.xpath('//@data-rate').extract()

        if Rate:
            item['Rate'] = float(Rate[0])
        else:
            item['Rate'] = "None"
        
        Gender = response.xpath('//div[@class = "product-info__tags"]/a/text()').extract()    
        if Gender:
            Gender = ''.join([g.strip() for g in Gender])
            item['Gender'] = Gender
        else:
            item['Gender'] = "None"
        
        yield item



    



