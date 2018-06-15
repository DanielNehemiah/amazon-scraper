# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 14:32:46 2018

@author: Daniel.C
"""

from lxml import html  
import json
import requests
import json,re
from dateutil import parser as dateparser
from time import sleep

#Add your own ASINs here 
#AsinList = ['B013HN3Q3E','B00P2CK9HK','B000RVYW7E','B004F027MK','B00QNYW49M','B06XSLM5YZ']

def get_asin_list(amazon_catalog_url):
    print("Amazon Catalog URL: "+amazon_catalog_url)
    asin_list = []
    #amazon_catalog_url  = 'https://www.amazon.in/Electric-Bass-Guitars/b/ref=dp_bc_3?ie=UTF8&node=4654331031'
    #amazon_catalog_url = 'https://www.amazon.in/b/ref=s9_acss_bw_cg_musCat1_2b1_w?_encoding=UTF8&node=4581269031'
    
    # Add some recent user agent to prevent amazon from blocking the request 
    # Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    catalog_page = requests.get(amazon_catalog_url,headers = headers,verify=False)
    catalog_page_response = catalog_page.text
    catalog_parser = html.fromstring(catalog_page_response)
    
    # Find total number of pages in catalog
    XPATH_NUMBER_OF_PAGES  = '//span[@class="pagnDisabled"]/text()'
    catalog_number_of_pages = int(catalog_parser.xpath(XPATH_NUMBER_OF_PAGES)[0])
    print("Number of pages in catalog: "+str(catalog_number_of_pages))
    
    # Get asin list from page 1
    XPATH_PRODUCT_ASIN  = '//@data-asin'
    raw_product_asin = catalog_parser.xpath(XPATH_PRODUCT_ASIN)
    asin_list.extend(raw_product_asin)
    
    for i in range(2,catalog_number_of_pages+1):
        # Retrieve next page in catalog
        catalog_page = requests.get(amazon_catalog_url+'&page='+str(i),headers = headers,verify=False)
        catalog_page_response = catalog_page.text
        catalog_parser = html.fromstring(catalog_page_response)
        
        # Get asin list from next page
        XPATH_PRODUCT_ASIN  = '//@data-asin'
        raw_product_asin = catalog_parser.xpath(XPATH_PRODUCT_ASIN)
        asin_list.extend(raw_product_asin)
        
    return asin_list
    
def get_product_details(asin, catalog_category):
    print("Downloading and processing page http://www.amazon.in/dp/"+asin)
    amazon_url  = 'http://www.amazon.in/dp/'+asin
    # Add some recent user agent to prevent amazon from blocking the request 
    # Find some chrome user agent strings  here https://udger.com/resources/ua-list/browser-detail?browser=Chrome
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    page = requests.get(amazon_url,headers = headers,verify=False)
    page_response = page.text

    parser = html.fromstring(page_response)
    XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
    XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
    XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'

    XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
    XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
    XPATH_PRODUCT_PRICE  = '//span[@id="priceblock_ourprice"]/text()'
    XPATH_PRODUCT_OLD_PRICE = '//span[@class="a-text-strike"]/text()'
    
    raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
    product_price = ''.join(raw_product_price).replace(',','')

    raw_product_old_price = parser.xpath(XPATH_PRODUCT_OLD_PRICE)
    product_old_price = ''.join(raw_product_old_price).replace(',','')

    raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
    product_name = ''.join(raw_product_name).strip()
    total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
    ratings_dict = {}

    #grabing the rating  section in product page
    for ratings in total_ratings:
        extracted_rating = ratings.xpath('./td//a//text()')
        if extracted_rating:
            rating_key = extracted_rating[0] 
            raw_raing_value = extracted_rating[1]
            rating_value = raw_raing_value
            if rating_key:
                ratings_dict.update({rating_key:rating_value})

    data = {
                'asin':asin,
                'product_category': catalog_category,
                'ratings':ratings_dict,
                'url':amazon_url,
                'price':product_price,
                'name':product_name,
                'old_price':product_old_price,
            }
    return data

def StartScrapping():
    #Add your own ASINs here 
    #AsinList = ['B013HN3Q3E','B00P2CK9HK','B000RVYW7E','B004F027MK','B00QNYW49M','B06XSLM5YZ']
   amazon_catalog_url  = 'https://www.amazon.in/Electric-Bass-Guitars/b/ref=dp_bc_3?ie=UTF8&node=4654331031'
   catalog_category = 'Electric-Bass-Guitars';
   AsinList = get_asin_list(amazon_catalog_url)
   print(AsinList)
   print(str(len(AsinList))+" items found in scrapped category")
   
   extracted_data = []
   for asin in AsinList:
       extracted_data.append(get_product_details(asin,catalog_category))
       sleep(1)
   f = open('data.json','w')
   json.dump(extracted_data,f,indent=4)

if __name__ == '__main__':
    StartScrapping()