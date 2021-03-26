import os
import sys
import inspect
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from suburbs import getMelbourneSuburbs

current_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from server.entities.resteraunt import Restaurant

options = Options()
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
options.add_argument("--headless")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
# Bypass scrape protection
options.add_argument('user-agent={0}'.format(user_agent))
driver = webdriver.Chrome(ChromeDriverManager(
    chrome_type=ChromeType.GOOGLE).install(), options=options)


def scrape_zomato(event, context):
    for suburb in getMelbourneSuburbs():
        for i in range(1, 2):
            url = 'https://www.zomato.com/melbourne/{0}-restaurants?page={1}'.format(
                suburb.lower(), i)
            driver.get(url)
            print(url + '\n')
            results = driver.find_elements_by_class_name(
                "result-title")
            print(driver.title)

            # Loop Through Lists of Web Elements
            out_lst = []
            for result in results:
                url = result.get_attribute("href")
                out_lst.append(url)

            # Scrape the data by looping through entries in list
            for url in out_lst:
                driver.get(url)
                time.sleep(6)
                print('Accessing Webpage OK')

                # Restaurant Name
                try:
                    name_anchor = driver.find_element_by_tag_name('h1')
                    name = name_anchor.text
                    rest_name = name
                except NoSuchElementException:
                    name = "404 Error"
                    rest_name = name
                    pass

                print(f'Scraping Restaurant Name - {name} - OK')

                # Create DynamoDB entity or get existing entry
                try:
                    current_restaurant = Restaurant.get(
                        rest_name, "Zomato")
                except Restaurant.DoesNotExist:
                    current_restaurant = Restaurant(
                        rest_name, "Zomato")

                # Restaurant Area
                try:
                    rest_area_anchor = driver.find_element_by_xpath(
                        """/html/body/div[1]/div[2]/main/div/section[3]/section/section[1]/section[1]/a""")
                    rest_area_text = rest_area_anchor.text
                    rest_area = rest_area_text
                    print(
                        f'Scraping Restaurant Area - {name} - {rest_area_text} - OK')
                except NoSuchElementException:
                    pass

                # Restaurant Type
                try:
                    rest_type_list_string = ""
                    rest_type_eltlist = driver.find_elements_by_xpath(
                        """/html/body/div[1]/div[2]/main/div/section[3]/section/section[1]/section[1]/div/a""")
                except NoSuchElementException:
                    pass

                for rest_type_anchor in rest_type_eltlist:
                    rest_type_text = rest_type_anchor.text
                    rest_type_list_string = \
                        rest_type_list_string + ", " + \
                            rest_type_text if rest_type_list_string != "" else rest_type_text

                current_restaurant.types = rest_type_list_string
                print(
                    f'Scraping Restaurant Type - {name} - {rest_type_list_string} - OK')

                # Restaurant Rating
                try:
                    rest_rating_anchor = driver.find_element_by_xpath(
                        """/html/body/div[1]/div[2]/main/div/section[3]/section/section[2]/section/div[1]/p""")
                    rest_rating_text = rest_rating_anchor.text
                except NoSuchElementException:
                    rest_rating_text = "Not Rated Yet"
                    pass

                current_restaurant.rating = rest_rating_text
                print(
                    f'Scraping Restaurant Rating - {name} - {rest_rating_text} - OK')

                # Restaurant Review
                try:
                    rest_review_anchor = driver.find_element_by_xpath(
                        """/html/body/div[1]/div[2]/main/div/section[3]/section/section[2]/section/div[2]/p""")
                    rest_review_text = rest_review_anchor.text
                except NoSuchElementException:
                    rest_review_text = "Not Reviewed Yet"
                    pass

                current_restaurant.review = rest_review_text
                print(
                    f'Scraping Restaurant Review Counts - {name} - {rest_review_text} - OK')

                # Restaurant Price for 2
                try:
                    price_for_2_anchor = driver.find_element_by_xpath(
                        """/html/body/div[1]/div[2]/main/div/section[4]/section/section/article[1]/section[2]/p[1]""")
                    price_for_2_text = price_for_2_anchor.text

                except NoSuchElementException:
                    price_for_2_text = "No Price Data Found"
                    pass

                if (price_for_2_text[0:2] == 'Rp') or (price_for_2_text[0:2] == 'No'):
                    current_restaurant.price_for_two = price_for_2_text
                else:
                    price_for_2_anchor = driver.find_element_by_xpath(
                        """/html/body/div[1]/div[2]/main/div/section[4]/section/section/article[1]/section[2]/p[2]""")
                    price_for_2_text = price_for_2_anchor.text

                    if (price_for_2_text[0:2] == 'Rp') or (price_for_2_text[0:2] == 'No'):
                        current_restaurant.price_for_two = price_for_2_text
                    else:
                        price_for_2_anchor = driver.find_element_by_xpath(
                            """/html/body/div[1]/div[2]/main/div/section[4]/section/section/article[1]/section[2]/p[3]""")
                        price_for_2_text = price_for_2_anchor.text
                        current_restaurant.price_for_two = price_for_2_text

                print(
                    f'Scraping Restaurant Price for Two - {name} - {price_for_2_text} - OK')

                # Restaurant Address
                rest_address_anchor = driver.find_element_by_xpath(
                    """/html/body/div[1]/div[2]/main/div/section[4]/section/article/section/p""")
                rest_address_text = rest_address_anchor.text
                current_restaurant.address = rest_address_text
                print(
                    f'Scraping Restaurant Address - {rest_address_text} - OK')

                # Restaurant Phone
                rest_phone_anchor = driver.find_element_by_xpath(
                    """/html/body/div[1]/div/main/div/section[4]/section/article/p""")
                rest_phone_text = rest_phone_anchor.text
                current_restaurant.phone = rest_phone_text
                print(
                    f'Scraping Restaurant Phone - {rest_phone_text} - OK')

                # Restaurant Additional Information
                addt_info_list_string = ""
                try:
                    addt_info_bigelt = driver.find_element_by_xpath(
                        """/html/body/div[1]/div[2]/main/div/section[4]/section/section/article[1]/section[2]/div[3]""")
                    addt_info_eltlist = addt_info_bigelt.find_elements_by_tag_name(
                        'p')
                except NoSuchElementException:
                    addt_info_eltlist = ["No additional info"]
                    pass

                for addt_info_anchor in addt_info_eltlist:
                    if isinstance(addt_info_anchor, str):
                        addt_info_text = addt_info_anchor
                        addt_info_list_string = \
                            addt_info_list_string + ", " + addt_info_text \
                                if addt_info_list_string != "" else addt_info_list_string
                    else:
                        addt_info_text = addt_info_anchor.text
                        addt_info_list_string = \
                            addt_info_list_string + ", " + addt_info_text \
                                if addt_info_list_string != "" else addt_info_list_string

                current_restaurant.info = addt_info_list_string
                print(
                    f'Scraping Restaurant Additional Info - {name} - {addt_info_text} - OK')

                # Save to ORM
                for x in range(0, 4):
                    try:
                        current_restaurant.save()
                        str_error = None
                    except Exception as error:
                        str_error = str(error)

                    if str_error:
                        time.sleep(2)
                    else:
                        break

    driver.close()


if __name__ == '__main__':
    scrape_zomato()
