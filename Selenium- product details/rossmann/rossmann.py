
import os
from re import X
from tokenize import Number
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class Rossmann(webdriver.Firefox):
    def __init__(self, driver_path='/usr/bin/geckodriver', close =False, numbOfProd = 100, sec = 10):
        self.driver_path = driver_path
        self.Close = close
        self.numProducts = numbOfProd
        ser = Service(driver_path)
        options = webdriver.firefox.options.Options()
        options.headless = False
        super(Rossmann, self).__init__(options=options, service=ser)
        self.implicitly_wait(sec)
        self.maximize_window()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.Close:
            self.quit()

    def loadPage(self, pageLink):
        self.get(pageLink)

    def goToTab(self, tabName = "none"):
        PromoTab = self.find_elements_by_css_selector(
            'a[href="/promocje"]'
        )[1].find_element(By.XPATH, "./..")
        PromoTab.click()

    def resultsFromPage(self):
        producs_section = self.find_element(
            By.CSS_SELECTOR,
            'section[class="promotion-row-products container"]'
        ).find_elements(
                By.CLASS_NAME,
                value = 'tile-product__name')

        return(producs_section)

    def productFeatures(self):

        Info = []
        title = self.find_element(
            By.CLASS_NAME,
            value="product-info__name"
            )

        title = title.find_element(
            By.TAG_NAME,
            'h1'
            ).text


        ShortDesc = self.find_element(
            By.CLASS_NAME,
            value="product-info__name"
            )
        ShortDesc = ShortDesc.find_element(
            By.TAG_NAME,
            'h2'
            ).text
        

        RegularPrice = self.find_element(
            By.CLASS_NAME,
            value='regular'
        ).text

        PromoPrice = self.find_element(
            By.CLASS_NAME,
            value='promo'
        ).text

        try:
            Availability = self.find_element(
                By.XPATH,
                "//*[contains(text(), 'NIEDOSTĘPNY ONLINE')]"
            )
            Availability = "UNAVAILABLE ONLINE"
        except:
            Availability = "AVAILABLE ONLINE"

        Link = self.current_url

        Categories = self.find_elements(
            By.CLASS_NAME,
            "breadcrumb-item"
            )
        Category = []
        for cat in Categories:
            Category.append(cat.find_element(By.TAG_NAME, 'a').text)

        Category = '/'.join(Category[1:-1])
        

        Image = self.find_element(
            By.CLASS_NAME,
            value = 'product-img'
        )
        Image= Image.find_element(
            By.TAG_NAME,
            'img'
            ).get_attribute('src')
        
        try:
            Review = self.find_element(
                By.XPATH,
                "//div[@class='product-info d-flex']"
                ).find_elements(By.TAG_NAME, 'span')
            Rank = Review[0].get_attribute('data-rate')
            NumbOfReviews = Review[1].text
            
        except:
            Rank = "None"
            NumbOfReviews = "None"


        Info.append([title,
                    ShortDesc,
                    
                    RegularPrice,
                    PromoPrice,
                    Availability,
                    Category,
                    Rank,
                    NumbOfReviews,
                    Link,
                    Image])
        return(Info)

    def nextPage(self, num):
        #try:
        #Next = self.find_element(
        #    By.XPATH,
        #    "//a[@class='pages__last']//parent::a"
        #)
        Next = self.find_element(
            By.XPATH,
            "//a[@class='pages__last']/following-sibling::a"
        )
        
        print(Next.get_attribute('innerHTML'))
        N = self.find_element(
            By.XPATH,
            "//input[@type='number']"
        )
        #N.clear()
        
        #N.send_keys(Keys.chord(Keys.CONTROL, "a"))
        
        #N.send_keys(Keys.DELETE)
        #N.send_keys(Keys.CONTROL + 1)
        N.send_keys(num)
        
        print(N.get_attribute("value"))
        time.sleep(3)


        #Next.click()
        #WebDriverWait(self,30).until(EC.element_to_be_clickable(Next)).click()
        #except:
        #    return('End')



from selenium.webdriver.common.by import By
