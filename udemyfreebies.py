from bs4 import BeautifulSoup
import requests
import re
from headers import USER_AGENTS, ACCEPT_LANGUAGES
import random
import time
from urllib.parse import urlparse, parse_qs
import udemy
import arrow
from typing import Generator

def extractLinksFromURL(url:str,tag:str,class_:str)-> list:
    time.sleep(3)
    response = requests.get(url,headers={
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': random.choice(ACCEPT_LANGUAGES)
    })
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all anchor tags with a class
    elements = soup.find_all(tag, class_=class_)
    
    
    links = []
    # Extract the href attributes and print the links
    for element in elements:
        links.append(element.get('href'))

    # Replace the category with go
    new_links = []

    for link in links:
        parts = link.split("/")
        parts[3] = "out"
        new_link = "/".join(parts)
        new_links.append(new_link)
    return new_links
    

def getUdemyUrl(link:str)-> str:
    time.sleep(2)
    response = requests.get(link, headers={
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': random.choice(ACCEPT_LANGUAGES)
    })
    return response.url

def extract_coupon_code(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    coupon_code = query_params.get('couponCode')
    course_name = parsed_url.path.split('/')[-2]
    return (coupon_code[0] if coupon_code else None, course_name)


def scrape(fast:bool=False,**kwargs) -> Generator:
    """Scrape coupons from `UdemyFreebies.com`"""
    debug = kwargs['debug']
    collected = []
    valid=0

    debug.print(f"\nExtracting URLs from UdemyFreebies")
    for i in range(1,10):
        debug.print(f"\nExtracting URLs from UdemyFreebies page {i}...")
        results = extractLinksFromURL(f"https://www.udemyfreebies.com/free-udemy-courses/{i}",'a','button-icon')
        collected.extend(results)
        debug.print(f"Got {len(results)}! New total: {len(collected)}")
    debug.is_summary(f"Total scraped from UdemyFreebies: {len(collected)}")
    debug.print(f"\n\nExtracting URLs from UdemyFreebies")

    validation_start = arrow.utcnow()
    yield {'mode':'init', 'message':'Started validating courses...', "count":{len(collected)}, 'provider': 'udemyfreebies'}
    output = validate(collected,len(collected),fast,debug=debug)
    validation_elaped = debug.get_elapsed_time(validation_start,arrow.utcnow())
    
    for out in output:
        valid = valid+1
        yield {'mode':'stream', "results":out}
    
    debug.print(f'Validation elapsed time: {validation_elaped}')
    debug.print(f'Successfully validated {valid}/{len(collected)} coupons')
    debug.is_summary(f'Validated: {valid}/{len(collected)} FREE coupons')
    debug.is_summary(f'Validation duration: {validation_elaped}')


def validate(data:list, count:int, fast:bool, **kwargs)-> Generator:
    debug = kwargs['debug']
    valid = []
    for c in data:
        url = getUdemyUrl(c)
        couponcode,course_name = extract_coupon_code(url)
        _course_name = course_name.replace('-',' ').title()
        debug.print(f'\n### Started validating -> {_course_name}')
        if couponcode:
            try:
                course_details, coupon_details = udemy.getUdemyData(course_name,couponcode,fast,debug=debug)
            except TypeError:
                debug.print('!! Skipped... Reason: Unreachable url')
                continue
            try:
                amount = coupon_details['price_text']['data']['pricing_result']['price']['amount']
                original_price = coupon_details['price_text']['data']['pricing_result']['list_price']['amount']
                _course_name = coupon_details['slider_menu']['data']['title']
            except KeyError:
                debug.print('!! Skipped... Reason: Course unavailable.')
                continue
            if not original_price: #if original price is $0
                debug.print('!! Skipped... Reason: listed for $0')
                continue
            if not amount: #if Free
                valid.append(_course_name)
                # valid.append({'details':course_details, 'coupon':coupon_details})
                debug.is_successful({"name":_course_name, "coupon":couponcode})
                debug.print(f'$$$ Successful -> {_course_name}')
                yield {
                    "url": f'https://www.udemy.com/course/{course_name}/?couponCode={couponcode}',
                    "course_id":course_details['id'],
                    "title": course_details['title'],
                    "coupon":couponcode,
                    "uses_remaining":coupon_details['price_text']['data']['pricing_result']['campaign']['uses_remaining'],
                    "maximum_uses":coupon_details['price_text']['data']['pricing_result']['campaign']['maximum_uses'],
                    "list_price":coupon_details['price_text']['data']['pricing_result']['list_price']['amount'],
                    "amount":coupon_details['price_text']['data']['pricing_result']['price']['amount'],
                    "currency_symbol":coupon_details['price_text']['data']['pricing_result']['price']['currency_symbol'],
                }
            else:
                debug.print('!! Skipped... Reason: Not free anymore.')
                continue
        else:
            debug.print('!! Skipped... Reason: No coupon code.')
            continue
        
    debug.is_summary(f"\nTotal valid: {len(valid)}/{count}")
    debug.print(f"\nNice: {len(valid)}/{count} validated!")
