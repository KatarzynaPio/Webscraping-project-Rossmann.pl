from rossmann.rossmann import Rossmann
import time
import math
from prettytable import PrettyTable
from selenium.webdriver.common.by import By

numberOfProducts = 7
PageToScrape = math.ceil(numberOfProducts/24)

print('Number of pages to scrape: {}'.format(PageToScrape))

try:
    ros = Rossmann()
    ros.loadPage("https://www.rossmann.pl")
    ros.goToTab() 
   
    AllProducts = []
    prodCount = 0
    for i in range(1, PageToScrape + 1):
        print('\n*** LOAD PRODUCTS FROM PAGE NUMBER {} ***\n'.format(i))
        productLinks = ros.resultsFromPage()
        for prod in productLinks:
            prodCount += 1
            if prodCount > numberOfProducts:
                break 
            link = prod.get_attribute('href').strip()
            ros2 = Rossmann( sec=3)
            print('Load Product {}/{} \n{}\n'.format(prodCount,numberOfProducts, link))
            ros2.loadPage(link)
            #time.sleep(5)
            features = ros2.productFeatures()
            AllProducts.append(features[0])
            ros2.quit()
        
        #ros.nextPage(num= i)
    print(AllProducts)
    table = PrettyTable(
        field_names=['title',
                    'ShortDesc',
                    'RegularPrice',
                    'PromoPrice',
                    'Availability',
                    'Category',
                    'Rank',
                    'NumbOfReviews',
                    'Link',
                    'Imag']
    )
    table.add_rows(AllProducts)
   # print(table)
    
except:
    pass





    
