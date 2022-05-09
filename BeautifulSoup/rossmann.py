#spr nastepny produkt,  
#Reading product 1456/6393.
#https://www.rossmann.pl/Produkt/Skora-wlosy-i-paznokcie/Altapharma-suplement-diety-biotyna-300-µg-40-szt,395129,9016 #
# UnicodeEncodeError: 'ascii' codec can't encode character '\xb5' in position 76: ordinal not in range(128)
from unicodedata import category
from urllib import request
from bs4 import BeautifulSoup as BS
import pandas as pd
import re
from urllib.error import HTTPError
from urllib.error import URLError
import time
import os
import urllib.parse

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
    except UnicodeEncodeError as e:
        try:
            urlNew = urllib.parse.urlsplit(url)
            urlNew = list(urlNew)
            urlNew[2] = urllib.parse.quote(urlNew[2],safe='/,')
            urlNew = urllib.parse.urlunsplit(urlNew)
            html = request.urlopen(urlNew)
            soup = BS(html.read(), 'html.parser')
            return soup
        except:
            print("'ascii' codec can't encode character in the link: \n {}".format(url))
            return 0
    else:
        soup = BS(html.read(), 'html.parser')
        return soup

def safe_str(obj):
    try: return str(obj)
    except UnicodeEncodeError:
        return obj.encode('ascii', 'ignore').decode('ascii')
    return ""


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
                'link':mainUrl + safe_str(bsProduct.find('a',class_ = 'tile-product__name')['href']),
                'regularPrice': ''
            }
            try:
                dProduct['regularPrice'] = bsProduct.find(class_ = 'tile-product__old-price').text
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

    Prod = {}
    soup = getdata(dProduct['link']) # Download the page for the product 
    if soup == 0:
        return 0
    try:
        Prod['name'] = soup.find('div',class_ = 'product-info__name').h1.text
    except: Prod['name'] ="None"
    
    try:
        Prod['image'] = 'https:' + str(soup.find('div',class_ = 'product-img').img['src'])
    except: Prod['image'] ="None"

    try:
        Prod['shortDescription'] = soup.find('div',class_ = 'product-info__name').h2.text
    except: Prod['shortDescription'] = "None"
    
    try:
        Prod['longDescription'] = soup.find('div',class_ = 'product__desctiption').find(class_ = 'accordion').div.text
    except: Prod['longDescription'] = "None"
    
    Prod['regularPrice'] = dProduct['regularPrice']
    Prod['promoPrice'] = dProduct['promoPrice'] 
    Prod['link'] = dProduct['link'] 
    # scrape additional info about product
    
    # If you can't find the word "NOT AVAILABLE ONLINE" on the page, 
    # it means that the product is available to order online, otherwise it is not available.
    if  soup.find_all(text='NIEDOSTĘPNY ONLINE'):  
        Prod['availability']  = "NIEDOSTĘPNY ONLINE"
    else:
        Prod['availability']  = "DOSTĘPNY ONLINE"
    
    # save the information about the categories in which the product is placed
    try:
        categories = soup.find_all(class_= 'breadcrumb-item')
        categoriesList = [category.a.text for category in categories[1:-1]]
        Prod['categories'] = "/".join(categoriesList)
        Prod['countCategories'] = len(categoriesList)
    except:
        Prod['categories'] = "None"
        Prod['countCategories'] = "None"

    # collect info about the review
    try:
        review = soup.find(class_= 'product-info__rate d-flex py-2').find_all('span')
        if review:
            Prod['rate'] = review[0]['data-rate']
            Prod['numberOfReviews'] = review[1].text
        else:
            Prod['rate'] = "None"
            Prod['numberOfReviews'] = "None"
    except:
            Prod['rate'] = "None"
            Prod['numberOfReviews'] = "None"
    
    try:      
            if soup.find(class_= 'product-info__tags').text:
                Prod['gender'] = soup.find(class_= 'product-info__tags').text
            else:
                Prod['gender'] = "None"
    except:
            Prod['gender'] = "None"
    
    return Prod

####################
### Main program ###
####################

# get the start time
st = time.time()

fileName = "AllProducts.csv"
ifSave = True
directory = os.getcwd()
ProdNotLoaded = []

numberOfProductsMax = 100000000 # # the maximum number of products for which the program should scrape data
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

#lProducts[0]['link'] = 'https://www.rossmann.pl/Produkt/Ozdoby-do-wlosow/For-Your-Beauty-Ozdoby-do-wlosow-#FYB-Gumki-do-wlosow-czarne-MICHAELA-15-szt-1,219919,8678'
for Product in lProducts:
    print('Reading product {}/{}.\n {} \n'.format(i, N, Product['link']))
    dProduct = getInfoAboutProduct(Product)
    if dProduct == 0:
        ProdNotLoaded.append(Product['link'])
    else:
        Products.append(dProduct)
    i += 1

Log = []
print('\n\n---------------------')
print('Status of the program:')
print('---------------------')
# save data as an external csv file 
if ifSave:
    if Products:
        df = pd.DataFrame(Products)
#        numberOfCatCols = max( df['countCategories'])
#        if df.countCategories < numberOfCatCols:
#            for i in range(numberOfCatCols - df.countCategories):
#                df.countCategories =  df.countCategories + '/'

#        print(df.categories.str.split(pat='/',expand=True))
#        df[['Cat1', 'Cat2', 'Cat3']] = df.categories.str.split(pat='/',expand=True)
        df.to_csv(fileName)
        pathToFile = os.path.join(directory,fileName)
        msg  = "Scraped data was saved here: {}".format(pathToFile)
        Log.append(msg)
        print()
    else:
        msg = "No data to save as an external file"
        Log.append(msg)
        print(msg)
else:
    msg = 'Data was scraped but do not saved anywhere'
    Log.append(msg)
    print(msg)

msg = 'Number od scraped products: {}'.format(len(Products))
Log.append(msg)
print(msg)

# get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
msg = 'Execution time: {} seconds.'.format(round(elapsed_time,4))
Log.append(msg)
print(msg)

msg = 'Execution time: {} seconds.'.format(round(elapsed_time/60,4))
Log.append(msg)
print(msg)

print('\n\n------------------------------------')
msg = 'Products that have not been scraped:'
Log.append(msg)
print(msg)
print('------------------------------------')

if ProdNotLoaded:
    for prod in ProdNotLoaded:
        msg = '    * {}'.format(prod)
        Log.append(msg)
        print(msg)
else:
    msg = 'None'
    Log.append(msg)
    print(msg)

fileName = 'log.txt'
with open(fileName, mode="w") as f:  # also, tried mode="rb"
    for line in Log:
        f.write("%s\n" % line)

print('\nLog file is saved here: ' , os.path.join(directory,fileName))

