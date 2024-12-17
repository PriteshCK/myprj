from django.shortcuts import render
from django.http import JsonResponse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-images")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--force-device-scale-factor=0.1")
chrome_options.add_argument("headless")
chrome_options.add_argument("--window-size=3840,2160")


def scrape_places(query):
    driver = webdriver.Chrome(options=chrome_options)
    search_url = "https://www.google.com/maps/search/" + query

    driver.get(search_url)
    driver.implicitly_wait(10)


    # Scroll sidebar
#    scrollable_div = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
#    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
#    
#    while True:
#        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
#        time.sleep(5)
#        
#        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
#        if new_height == last_height:
#            break
#        last_height = new_height

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    target_class = "Nv2PK"
    elements = soup.find_all(class_=target_class)

    urls = []
    for element in elements:
        a_tags = element.find_all('a', href=True)
        for a_tag in a_tags:
            href = a_tag['href']
            if "https://www.google.com/maps/place" in href:
                urls.append(href)

    print("Got " + str(len(urls)) + " places.")
    driver.quit()
    return urls


def save_places_to_file(urls):
    with open('places.txt', 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(url + '\n')


def scrape_data_from_url(url):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    result = {
        "url": url,
        "name": None,
        "address": None,
        "website": None,
        "phone": None
    }

    # Name
    node = soup.find(class_="DUwDvf")
    if node:
        result["name"] = node.text

    # Address
    button_add = soup.find('button', attrs={'aria-label': lambda x: x and 'Address:' in x})
    if button_add:
        result["address"] = button_add['aria-label'].replace("Address: ", "").strip()

    # Website
    a_site = soup.find('a', attrs={'aria-label': lambda x: x and 'Website:' in x})
    if a_site:
        result["website"] = a_site['aria-label'].replace("Website: ", "").strip()

    # Phone
    button_phone = soup.find('button', attrs={'aria-label': lambda x: x and 'Phone:' in x})
    if button_phone:
        result["phone"] = button_phone['aria-label'].replace("Phone: ", "").strip()

    driver.quit()
    return result


def scrape_all_places():
    with open('places.txt', 'r', encoding='utf-8') as file:
        urls = [url.strip() for url in file.readlines()]

    results = []
    total_urls = len(urls)
    for index, url in enumerate(urls, start=1):
        print(f"[{index}/{total_urls}] Scraping: {url}")
        result = scrape_data_from_url(url)
        results.append(result)

    return results


def scrape_api(request):
    query = request.GET.get('query') or request.POST.get('query')
    print("Searching for: " + query + "...")
    urls = scrape_places(query)
    save_places_to_file(urls)
    results = scrape_all_places()
    return JsonResponse(results, safe=False, json_dumps_params={'indent': 4, 'ensure_ascii': False})

