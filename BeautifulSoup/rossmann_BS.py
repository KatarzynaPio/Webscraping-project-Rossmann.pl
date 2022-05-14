from urllib import request
from bs4 import BeautifulSoup as BS
import pandas as pd
from urllib.error import HTTPError
from urllib.error import URLError
import time
import os
import urllib.parse

################
## CONSTANTS  ##
################
FILE_NAME = "results_BS_120.csv"
FILE_NAME_LOG = 'log_BS_120.txt'
IF_SAVE = True
DIRECTORY = os.getcwd()
NUM_OF_PROD_MAX = 120 # the maximum number of products for which the program should scrape data
MAIN_ULR = 'https://www.rossmann.pl'
SAVE_BY = 50 # This variable specifies every how many products data frame with scraped data
             # should  be written to the external file and the memory
             # freed by clearing the list that holds the detailed information about the products.


#################
### FUNCTIONS ###
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
                'link':MAIN_ULR + str(bsProduct.find('a',class_ = 'tile-product__name')['href']),
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
            print("!!!!ERROR!!!! cannot load the link to the product. It is skipped...")
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
        Prod['Name'] = soup.find('div',class_ = 'product-info__name').h1.text
    except: Prod['Name'] ="None"
    
    try:
        Prod['Image'] = 'https:' + str(soup.find('div',class_ = 'product-img').img['src'])
    except: Prod['Image'] ="None"

    try:
        Prod['Description'] = soup.find('div',class_ = 'product-info__name').h2.text
    except: Prod['Description'] = "None"
    
    Prod['RegularPrice'] = dProduct['regularPrice'].replace(',', '.').replace('zł','').strip()
    Prod['PromoPrice'] = dProduct['promoPrice'].replace(',', '.').replace('zł','').strip()
    Prod['Link'] = dProduct['link'] 


    # scrape additional info about product
    
    # If you can't find the word "NOT AVAILABLE ONLINE" on the page, 
    # it means that the product is available to order online, otherwise it is not available.
    if  soup.find_all(text='NIEDOSTĘPNY ONLINE'):  
        Prod['Availability']  = "Unavailable online"
    else:
        Prod['Availability']  = "Available online"
    
    # save the information about the categories in which the product is placed
    try:
        categories = soup.find_all(class_= 'breadcrumb-item')
        categoriesList = [category.a.text for category in categories[1:-1]]
        Prod['Categories'] = "/".join(categoriesList)
    except:
        Prod['Categories'] = "None"

    # collect info about the review
    try:
        review = soup.find(class_= 'product-info__rate d-flex py-2').find_all('span')
        if review:
            Prod['Rate'] = review[0]['data-rate']
            NumberOfReviews = review[1].text.strip()
            Prod['NumberOfReviews'] = NumberOfReviews[1:-1].split(' ')[0]
        else:
            Prod['Rate'] = "None"
            Prod['NumberOfReviews'] = "None"
    except:
            Prod['Rate'] = "None"
            Prod['NumberOfReviews'] = "None"
    
    try:      
            if soup.find(class_= 'product-info__tags').text:
                Prod['Gender'] = soup.find(class_= 'product-info__tags').text.strip()
            else:
                Prod['Gender'] = "None"
    except:
            Prod['Gender'] = "None"
    
    return Prod

def saveResultsCSV(FileName,ProdList, FirstDFtoSave = False):
    '''
    Function changes ProdList to data frame and save it to external csv file 
    If FirstDFtoSave is tru new FileName is crated otherwise  new rows are added to the FileName 
    '''

    if FirstDFtoSave:
        df = pd.DataFrame(ProdList)
        df.to_csv(FileName,index=False)
        
    else:
        df = pd.DataFrame(ProdList)
        df.to_csv(FileName, mode='a', index=False, header=False)


####################
### MAIN PROGRAM ###
####################

# get the start time
st = time.time()

ProdNotLoaded = [] # list to track product which were for some reason not been scraped 
bs = getdata(MAIN_ULR)

# ---------------------------------------------------
# find the tab with "Promocje"/"Promotions"
# since we cannot click the "Next Page" button or
#  retrieve the link assigned to it, we need to 
# add the "?Page=1&PageSize=24" part to the link and
#  manipulate the page number by changing this url part
# ---------------------------------------------------
salesUrl = MAIN_ULR + str([span for span in bs.find_all('a',class_='nav__link') if span.text == "Promocje"][0]['href']) + '?Page=1&PageSize=24'
bsSales = getdata(salesUrl) 
NumberOfPages = int(bsSales.find(class_= 'pages__last').text) # number of pages found in the Promotions tab
lProducts = [] # list with all products from Promotions tab 

# ---------------------------------------------------
# load products from each page in the Promotions tab
# ---------------------------------------------------
for page in range(1,NumberOfPages + 1):
    print('Load List of Products from Promotion Page {}/{}. \n {}'.format(page, NumberOfPages, salesUrl))
    ProductsOnPage = loadLinksToProductFromPage(bsSales) # load product from given page in the Promotion tab
    lProducts = lProducts + ProductsOnPage
    print('Number of products on page {}.\n'.format(len(ProductsOnPage)))
    # stop load the products if we reach the max number of Products we would like to load
    if len(lProducts) >NUM_OF_PROD_MAX:
        break
    salesUrl = salesUrl.replace('Page=' + str(page),'Page=' +str(page + 1) )
    bsSales = getdata(salesUrl)
    
# ---------------------------------------------------
# limit the number of products to scarpe fully to the
#  number given as the maximum
# ---------------------------------------------------
if len(lProducts) >NUM_OF_PROD_MAX:
    lProducts = lProducts[:NUM_OF_PROD_MAX]

N = len(lProducts)
n = 0 # number of products scraped correctly 
Products  = []
Products_time = [] # list to measure the time of scraping info about one product
i = 1
First = True
# ---------------------------------------------------
# scrape and save all information about all products 
# linked in the lProducts list
# ---------------------------------------------------
for Product in lProducts:
    print('Reading product {}/{}.\n {} \n'.format(i, N, Product['link']))

    st_prod = time.time() # start measuring the time of scraping info about one product
    dProduct = getInfoAboutProduct(Product)
    et_prod = time.time()
    time_prod = round(et_prod - st_prod, 4)
    Products_time.append(time_prod)

    if dProduct == 0:
        ProdNotLoaded.append(Product['link'])
    else:
        Products.append(dProduct)
        n += 1
    # save information from list Products to the external file FILE_NAME 
    if IF_SAVE :
        if len(Products) >= SAVE_BY: # if the number of products for which data has 
                                     # been scraped exceeds a given limit, save
                                     # the current data to an external file and release the memory
            if First: 
                # create file/ overwrite existing one
                saveResultsCSV(FileName=FILE_NAME,ProdList=Products, FirstDFtoSave=True)
                First = False
            else:
                # append data to exisitng file 
                saveResultsCSV(FileName=FILE_NAME,ProdList=Products)
            Products = []
    i += 1

# ---------------------------------------------------
# The code below is related to creating result
# csv file and log file and printing final mesages 
# ---------------------------------------------------

Log = []  # list which elements will be the lines of log file, which save basic info about program execution
print('\n\n---------------------')
print('Status of the program:')
print('---------------------')

# save data as in external csv file if it is still something to save in the list Products 
if IF_SAVE:
    if First == True and len(Products) != 0: # it means number of scraped products is higer than 0 and lowet than SAVE_BY limit 
            saveResultsCSV(FileName=FILE_NAME,ProdList=Products,FirstDFtoSave=True)
            pathToFile = os.path.join(DIRECTORY,FILE_NAME)
            msg  = "Scraped data are saved: {}".format(pathToFile)
            Log.append(msg)
            print(msg, '\n')
    
    elif First == False and len(Products)>0: # it means that some data about scraped products have been save but still something left to save 
            saveResultsCSV(FileName=FILE_NAME,ProdList=Products)
            pathToFile = os.path.join(DIRECTORY,FILE_NAME)
            msg  = "Scraped data are saved: {}".format(pathToFile)
            Log.append(msg)
            print(msg, '\n')
    elif First == True and len(Products)==0:
        msg = "No data to save as an external file"
        Log.append(msg)
        print('\n', msg)
else:
    msg = 'Data was scraped but do not saved anywhere'
    Log.append(msg)
    print(msg, '\n')

msg = 'Number od scraped products: {}'.format(n)
Log.append(msg)
print(msg)

# get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
msg = 'Execution time sec: {}'.format(round(elapsed_time,4))
Log.append(msg)
print(msg)

msg = 'Execution time min: {}'.format(round(elapsed_time/60,4))
Log.append(msg)
print(msg)

msg = 'Average time of scraping data for one product sec: {}'.format(round(sum(Products_time)/len(Products_time),4))
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


with open(FILE_NAME_LOG, mode="w") as f:  # also, tried mode="rb"
    for line in Log:
        f.write("%s\n" % line)

print('\nLog file is saved: ' , os.path.join(DIRECTORY,FILE_NAME_LOG), '\n')

