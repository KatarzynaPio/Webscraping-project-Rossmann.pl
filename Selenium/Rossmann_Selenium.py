from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from csv import writer


### CSV ###
def AddToCSV(List):
    with open("results.csv", "a+", newline='') as output_file:
        csv_writer = writer(output_file)
        csv_writer.writerow(List)

#How many pages you want to be scraped? The number current has been set to "1". You can change to any number.
pgnumber = 1

#Starting to measure timing
st = time.time()

##################
#The Main Program#
#################
for page in range(1, pgnumber+1):
    page_url = "https://www.rossmann.pl/promocje?Page=" + str(page)
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.maximize_window()
    browser.get(page_url)
    ### Finds all the products on the page
    elements = WebDriverWait(browser, 10).until(EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="row inspirations"]/div/div[@class="tile-product"]/a[@class="tile-product__name"]')))
    
    ### Starting to scrape each product page
    for element in elements:
            href = element.get_attribute('href')
            print(href)
            #Open new window with specific href
            browser.execute_script("window.open('" +href +"');")
            #Switch to new window
            browser.switch_to.window(browser.window_handles[1])

            #Scraped details
            Name = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'h1'))).text
            Old_Price = browser.find_element(By.XPATH, value='//span[@class="regular"]').text
            New_Price = browser.find_element(By.XPATH, value='//span[@class="promo"]').text
            ShortDesc = browser.find_element(By.CLASS_NAME,value="product-info__name")
            ShortDesc = ShortDesc.find_element(By.TAG_NAME,'h2').text
            try:
                Availability = browser.find_element(By.XPATH,"//*[contains(text(), 'NIEDOSTĘPNY ONLINE')]")
                Availability = "UNAVAILABLE ONLINE"
            except:
                Availability = "AVAILABLE ONLINE"

            Categories = browser.find_elements(
            By.CLASS_NAME,
            "breadcrumb-item"
            )
            Category = []
            for cat in Categories:
                Category.append(cat.find_element(By.TAG_NAME, 'a').text)
            Category = '/'.join(Category[1:-1])

            Link = href
            
            Image = browser.find_element(By.CLASS_NAME,value = 'product-img')
            Image= Image.find_element(By.TAG_NAME,'img').get_attribute('src')

            try:
                Review = browser.find_element(By.XPATH,"//div[@class='product-info d-flex']").find_elements(By.TAG_NAME, 'span')
                Rate = Review[0].get_attribute('data-rate')
                NumbOfReviews = Review[1].text
            
            except:
                Rate = "None"
                NumbOfReviews = "None"

            
            #Saving to CSV
            row_list = [Name, Old_Price, New_Price, ShortDesc, Link, Availability, Category, Image, NumbOfReviews, Rate]
            AddToCSV(row_list)

            #Close the new window
            browser.close()
            #Back to main window
            browser.switch_to.window(browser.window_handles[0])
        
#Finish time
et = time.time()

#Measuring the scraping time
elapsed_time = et - st
sec = 'Execution time: {} seconds.'.format(round(elapsed_time,4))
print(sec)
min = 'Execution time min: {}'.format(round(elapsed_time/60,4))
print(min)
#End of the scraping
browser.close()
