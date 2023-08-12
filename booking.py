from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import logging
from selenium.webdriver.common.by import By
import selenium
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime as dt

from utils.functions import prepare_driver

DOMAIN = 'https://www.booking.com'
logger = logging.getLogger()


def prepare_driver(url):
    '''Returns a Firefox Webdriver.'''
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.headless = True

    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)

    # print("instanciou o driver")
    driver.get(url)
    # print("fez o get")
    return driver


class BListing():
    """
    # BListing represents an Airbnb room_id, as captured at a moment in time.
    # room_id, survey_id is the primary key.
    """

    def __init__(self, config, driver, url, survey_id, checkin_date, checkout_date):
        self.config = config

        self.room_id = None
        self.room_name = None
        self.accommodates = None
        self.price = None
        self.bedtype = None
        self.latitude = None
        self.longitude = None
        self.avg_rating = None
        self.comodities = None
        self.hotel_name = None
        self.localized_address = None
        self.property_type = None
        self.reviews = None
        self.survey_id = survey_id
        self.checkin_date = checkin_date
        self.checkout_date = checkout_date
        self.hotel_id = None

        self.start_date = dt.date.today() + dt.timedelta(days=15)
        self.finish_date = dt.date.today() + dt.timedelta(days=16)
        self.location_id = None

    def find_hotel_name(self, driver):
        try:
            element = driver.find_element(By.CSS_SELECTOR, '.pp-header__title')
            self.hotel_name = element.text
        except selenium.common.exceptions.NoSuchElementException:
            raise

    def find_localized_address(self, driver):
        try:
            element = driver.find_element(
                By.CSS_SELECTOR, '.js-hp_address_subtitle')
            self.localized_address = element.text
        except selenium.common.exceptions.NoSuchElementException:
            raise

    def find_room_informations(self, driver):
        try:
            table_rows = driver.find_elements(
                By.XPATH, "//*[@id='hprt-table']/tbody/tr")
            for row in table_rows:
                try:
                    room_name = row.find_element(
                        By.CLASS_NAME, 'hprt-roomtype-link')
                    self.room_name = room_name.text
                    self.room_id = room_name.get_attribute("data-room-id")

                    bed_type = row.find_element(
                        By.CSS_SELECTOR, '.hprt-roomtype-bed')
                    self.bedtype = bed_type.text
                except selenium.common.exceptions.NoSuchElementException:
                    pass

                accomodates = row.find_elements(
                    By.CSS_SELECTOR, ".bicon-occupancy")
                self.accomodates = len(accomodates)

                # preco
                price = row.find_element(
                    By.CSS_SELECTOR, '.bui-price-display__value')
                self.price = price.text.split('R$ ')[1]
        except selenium.common.exceptions.NoSuchElementException:
            raise

    def find_latlng(self, driver):  # ok
        try:
            element = driver.find_element(By.ID, 'hotel_header')
            coordinates = element.get_attribute('data-atlas-latlng').split(',')
            self.latitude = coordinates[0]
            self.longitude = coordinates[1]
        except selenium.common.exceptions.NoSuchElementException:
            raise

    def find_hotel_id(self, url):
        name = url.split('www.booking.com/hotel/br/')[1]
        name = name.split('.pt-br')[0]
        print(name)
        self.hotel_id = name

    def find_property_type(self, driver):
        try:
            element = driver.find_element(
                By.XPATH, '//*[@data-testid="property-type-badge"]')
            self.property_type = element.text
        except selenium.common.exceptions.NoSuchElementException:
            raise

    def find_overall_classification(self, driver):
        try:
            element = driver.find_element(
                By.CSS_SELECTOR, 'div.b5cd09854e.d10a6220b4')
            if ',' in element.text:
                self.avg_rating = float(element.text.replace(',', '.'))
            else:
                if len(element.text) > 0:
                    self.avg_rating = float(element.text)
        except selenium.common.exceptions.NoSuchElementException:
            raise
        except:
            raise

    def find_principal_comodities(self, driver):
        try:
            element = driver.find_elements(
                By.CSS_SELECTOR, 'div.a815ec762e.ab06168e66')
            comodities = []
            for comodity in element:
                comodities.append(comodity.text)

            self.comodities = comodities
        except selenium.common.exceptions.NoSuchElementException:
            raise

    def find_reviews_quantity(self, driver):
        try:
            element = driver.find_element(By.XPATH, '//*[@rel="reviews"]')
            if element.text is not None:
                r = element.text.split(
                    'Avaliações de hóspedes (')[1].split(')')[0]
                self.reviews = float(r)
        except selenium.common.exceptions.NoSuchElementException:
            raise
        except:
            raise

def go_to_next_page(driver, page):
    try:
        page.click()
    except selenium.common.exceptions.ElementClickInterceptedException:
        btn = driver.find_element(
            By.CSS_SELECTOR, '.fc63351294.a822bdf511.e3c025e003.fa565176a8.f7db01295e.c334e6f658.ae1678b153')
        btn.click()
        page.click()
    print("clicou")


def search_booking_rooms(area, start_date, finish_date, survey_id, config=None,):
    print("Buscando no bookind")
    city = area.split(',')[0]

    checkin_date = start_date
    if checkin_date is None:
        checkin_date = dt.date.today() + dt.timedelta(days=15)

    checkout_date = finish_date
    if checkout_date is None:
        checkout_date = dt.date.today() + dt.timedelta(days=16)

    url = "https://www.booking.com/searchresults.pt-br.html?ss={}&ssne={}&ssne_untouched={}&checkin={}&checkout={}".format(
        city, city, city, checkin_date, checkout_date)
    driver = prepare_driver(url)
    print("aqui")

    wait = WebDriverWait(driver, timeout=10).until(
        EC.presence_of_all_elements_located(
                        (By.XPATH, '//*[@data-testid="property-card"]')))
    # FIND ALL PAGES
    all_pages = driver.find_elements(By.CLASS_NAME, 'f32a99c8d1')
    print("as pages: ", all_pages)
    for page in all_pages[1:len(all_pages):1]:
        print(page)

        for i in range(10):
            try:
                logger.debug("Attempt " + str(i+1) + " to find page")
                property_cards = driver.find_elements(
                    By.XPATH, '//*[@data-testid="property-card"]//*[@data-testid="title-link"]')
                urls = []
                for property_card in property_cards:
                    urls.append(property_card.get_attribute("href"))

                print("as urls: ", urls)
                for url in urls:
                    # print(url)
                    hotel_page = prepare_driver(url)

                    listing = BListing(config, driver, url,
                                       survey_id, checkin_date, checkout_date)

                    listing.find_hotel_id(url)
                    listing.find_latlng(hotel_page)
                    listing.find_principal_comodities(hotel_page)
                    listing.find_hotel_name(hotel_page)
                    listing.find_localized_address(hotel_page)
                    listing.find_reviews_quantity(hotel_page)
                    listing.find_overall_classification(hotel_page)
                    # print("vem aqui")
                    # listing.find_property_type(hotel_page)
                    print("passa aqui")

                    listing.find_room_informations(
                        hotel_page)  # needs to be the last call
                    listing.save(False)

                go_to_next_page(driver, page)
            except selenium.common.exceptions.TimeoutException:
                print("hmm")
                continue

    driver.quit()

def main():
    try:
        search_booking_rooms('Ouro Preto, Minas Gerais', None, None, 3, None)
        return "Deu tudo certo!"
    except Exception:
        logging.exception("Top level exception handler: quitting.")
        exit(0)


if __name__ == "__main__":
    main()
