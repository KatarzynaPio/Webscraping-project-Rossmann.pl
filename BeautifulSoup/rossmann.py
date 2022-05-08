#spr nastepny produkt,  
#Reading product 1456/6393.
#https://www.rossmann.pl/Produkt/Skora-wlosy-i-paznokcie/Altapharma-suplement-diety-biotyna-300-µg-40-szt,395129,9016 #
# UnicodeEncodeError: 'ascii' codec can't encode character '\xb5' in position 76: ordinal not in range(128)
from cgi    import test
from fileinput import filename
from typing import Type
from urllib import request
from bs4    import BeautifulSoup as BS
import pandas as pd
import re
from urllib.error import HTTPError
from urllib.error import URLError
import time
import os

#################
### Functions ###
#################
def getdata(url):
    '''
    Open url given as a function's argument and create a BeautifulSoup object 
    if HTTPError or URLError is occured than 0 value is returned otherwise BeautifulSoup object
    '''
    try:
        html = request.urlopen(url)
    except HTTPError as e:
        print(e)
        return 0
    except URLError as e:
        print("The server could not be found!")
        return 0
    else:
        soup = BS(html.read(), 'html.parser')
        return soup



def loadLinksToProductFromPage(bs):
    '''
    create a list of products that are listed on the page given  
    as a BeautifulSoup object in the function argument
    Each product is placed in returned list as a dictionary
    with keys such as link to the product page, 
    regular price of the product  and promotional price of the product .
    '''
    bsProducts = bs.find_all('div',class_='col-8 col-lg-4 mb-4 item') # locate each product window
    lProducts = [] # list to save dictionaries created for all products
    # create dictionary for each product with link, price after and before promotion
    for bsProduct in bsProducts:
        try:
            dProduct = {
                'link':mainUrl + str(bsProduct.find('a',class_ = 'tile-product__name')['href']),
            }
            try:
                dProduct['regularPrice'] = bsProduct.find(class_ = 'tile-product__old-price').text,
            except:
                dProduct['regularPrice'] = "None"
            try:
                dProduct['promoPrice'] = bsProduct.find(class_ = 'tile-product__promo-price').text
            except:
                dProduct['promoPrice'] = "None"

            lProducts.append(dProduct)
        except:
            print("!!!!ERROR!!!! cannot load the link to the product. It is skipped.")
        
    return(lProducts)


def getInfoAboutProduct(dProduct):
    '''
    Scrape additional product information from the product page 
    that is not visible on the page of list of all the products on the promotion. 
    The obtained information is stored as a dictionary.
    The value accepted by the function is a dictionary containing
    as one of its values a link to the product page.
    '''
    soup = getdata(dProduct['link']) # Download the page for the product 
    Product['Name'] = soup.find('div',class_ = 'product-info__name').h1.text
    Product['image'] = soup.find('div',class_ = 'product-img').img['src']
    Product['shortDescription'] = soup.find('div',class_ = 'product-info__name').h2.text
    Product['longDescription'] = soup.find('div',class_ = 'product__desctiption').find(class_ = 'accordion').div.text
    Product['regularPrice'] = dProduct['regularPrice'][0]
    Product['promoPrice'] = dProduct['promoPrice'] 

    # scrape additional info about product
    
    # If you can't find the word "NOT AVAILABLE ONLINE" on the page, 
    # it means that the product is available to order online, otherwise it is not available.
    if  soup.find_all(text='NIEDOSTĘPNY ONLINE'):  
        Product['availability']  = "NIEDOSTĘPNY ONLINE"
    else:
        Product['availability']  = "DOSTĘPNY ONLINE"
    
    # save the information about the categories in which the product is placed
    categories = soup.find_all(class_= 'breadcrumb-item')
    categoriesList = [category.a.text for category in categories[1:-1]]
    Product['categories'] = "/".join(categoriesList)
    
    # collect info about the review
    try:
        review = soup.find(class_= 'product-info__rate d-flex py-2').find_all('span')
        if review:
            Product['rate'] = review[0]['data-rate']
            Product['numberOfReviews'] = review[1].text
        else:
            Product['rate'] = "None"
            Product['numberOfReviews'] = "None"
    except:
            Product['rate'] = "None"
            Product['numberOfReviews'] = "None"
    
    try:      
            if soup.find(class_= 'product-info__tags').text:
                Product['gender'] = soup.find(class_= 'product-info__tags').text
            else:
                Product['gender'] = "None"
    except:
            Product['gender'] = "None"
        
    return Product

####################
### Main program ###
####################

# get the start time
st = time.time()

fileName = "200Products.csv"
directory = os.getcwd()

numberOfProductsMax = 100 # # the maximum number of products for which the program should scrape data
mainUrl = 'https://www.rossmann.pl'
bs = getdata(mainUrl)

# find the tab with "Promocje"/"Promotions"
# since we cannot click the "Next Page" button or retrieve the link assigned to it, we need to 
# add the "?Page=1&PageSize=24" part to the link and manipulate the page number by changing this url part
salesUrl = mainUrl + str([span for span in bs.find_all('a',class_='nav__link') if span.text == "Promocje"][0]['href']) + '?Page=1&PageSize=24'
bsSales = getdata(salesUrl) 
NumberOfPages = int(bsSales.find(class_= 'pages__last').text) # number of pages found in the Promotions tab
lProducts = [] # list with all products from Promotions tab 

# load products from each page in the Promotions tab 
for page in range(1,NumberOfPages + 1):
    print('Load List of Products from Promotion Page {}/{}. \n {}'.format(page, NumberOfPages, salesUrl))
    ProductsOnPage = loadLinksToProductFromPage(bsSales) # load product from given page in the Promotion tab
    lProducts = lProducts + ProductsOnPage
    print('Number of products on page {}.\n'.format(len(ProductsOnPage)))
    # stop load the products if we reach the max number of Products we would like to load
    if len(lProducts) >numberOfProductsMax:
        break
    salesUrl = salesUrl.replace('Page=' + str(page),'Page=' +str(page + 1) )
    bsSales = getdata(salesUrl)
    
#print(len(lProducts))

# limit the number of products to scarpe fully to the number given as the maximum
if len(lProducts) >numberOfProductsMax:
    lProducts = lProducts[:numberOfProductsMax]

N = len(lProducts)
Products  = []
i = 1
# scrape and save all information about all products linked in the lProducts list
for Product in lProducts:
    print('Reading product {}/{}.\n {} \n'.format(i, N, Product['link']))
    Products.append(getInfoAboutProduct(Product))
    i += 1

# save data as an external csv file 
df = pd.DataFrame(Products)
df.to_csv(fileName)
pathToFile = os.path.join(directory,fileName)
print("Scraped data was saved here: {}".format(pathToFile))

# get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
print('Execution time:', round(elapsed_time,4), 'seconds')
print('Execution time:', round(elapsed_time/60,4), 'minutes')

