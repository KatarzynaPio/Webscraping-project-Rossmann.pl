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

#This version works fine and loops pages and also the products.
#the only thing left is to add more product details.

def AddToCSV(List):
    with open("results.csv", "a+", newline='') as output_file:
        csv_writer = writer(output_file)
        csv_writer.writerow(List)

#How many pages you want to be scraped?
pgnumber = 3
for page in range(1, pgnumber+1):
    page_url = "https://www.rossmann.pl/promocje?Page=" + str(page)
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(page_url)
    elements = WebDriverWait(browser, 10).until(EC.visibility_of_all_elements_located((By.XPATH, '//div[@class="row inspirations"]/div/div[@class="tile-product"]/a[@class="tile-product__name"]')))
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
            Link = href
            
            #Pushing to CSV
            row_list = [Name, Old_Price, New_Price, Link]
            AddToCSV(row_list)

            #Close the new window
            browser.close()
            #Back to main window
            browser.switch_to.window(browser.window_handles[0])

browser.close()

