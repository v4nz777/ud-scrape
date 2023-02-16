import requests
from headers import USER_AGENTS, ACCEPT_LANGUAGES
from udemy import getUdemyData
from urllib.parse import urlparse, parse_qs
import random
import json
import time
import arrow
import re
from typing import Generator


URL = "https://www.real.discount/api-web/all-courses"

def scrape(free:int=1,fast:bool=False, **kwargs)-> Generator:
    """Scrape from `real.discount`"""
    valid = 0
    debug = kwargs['debug'] #kwargs.get('debug',Debug('start_scrape'))
    # Start Scraping Courses from real.discount
    scraping_start = arrow.utcnow()
    debug.print(f"Getting all FREE courses from REAL.DISCOUNT...")
    time.sleep(2)
    count = getFreeCourseCount()
    time.sleep(3)
    url = f"{URL}/?store=Udemy&page=1&per_page={count}&orderby=undefined&free={free}"
    response = requests.get(url, headers={
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': random.choice(ACCEPT_LANGUAGES)
    })
    result = json.loads(response.content)
    scraping_elapsed = debug.get_elapsed_time(scraping_start,arrow.utcnow())
    count = result['count']
    debug.print(f"Successfully scraped: {count} Udemy coupons(FREE)! | elapsed: {scraping_elapsed}")
    debug.is_summary(f"Total scraped from REAL.DISCOUNT: {count}")

    # Start Validation
    validation_start = arrow.utcnow()
    debug.print('Started validating courses...')
    yield {'mode':'init', 'message':'Started validating courses...', "count":{count}, 'provider': 'realdiscount'}
    output = validateCourses(result['results'],count,fast,debug=debug)
    validation_elaped = debug.get_elapsed_time(validation_start,arrow.utcnow())
    
    
    for out in output:
        valid = valid+1
        yield {'mode':'stream', "results":out}
    
    debug.print(f'Validation elapsed time: {validation_elaped}')
    debug.print(f'Successfully validated {valid}/{count} coupons')
    debug.is_summary(f'Validated: {valid}/{count} FREE coupons')
    debug.is_summary(f'Validation duration: {validation_elaped}')


def getFreeCourseCount(**kwargs)-> int:
    """Get all free courses from real.discount"""
    url=f"{URL}/?store=Udemy&page=1&per_page=1&orderby=undefined&free=1"
    response = requests.get(url, headers={
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': random.choice(ACCEPT_LANGUAGES)
    })
    result = json.loads(response.content)
    return result['count']


def extractUdemyUrl(url:str,**kwargs)-> tuple:
    debug = kwargs['debug'] #kwargs.get('debug', Debug('extract_url'))
    # Define a regular expression pattern to match the Udemy domain
    pattern = r"https?://(?:www\.)?udemy\.com/.*"

    # Search the URL for the pattern
    match = re.search(pattern, url)
    if match:
        # If the pattern is found, extract the matched portion of the URL
        udemy_url = match.group()
        
        # Extract the course name from the URL path using regular expression
        course_name = re.search(r'/course/([\w-]+)/?', udemy_url).group(1)

        # Extract the coupon code from the query string
        query_string = urlparse(udemy_url).query
        try:
            coupon_code = parse_qs(query_string)['couponCode'][0]
        except KeyError:
            
            return (None, None)
        return (course_name,coupon_code)

    else:
        # If the pattern is not found, print an error message
        debug.print("No Udemy URL found in the input.")
        return (None,None)


def validateCourses(data:list, count:int, fast:bool, **kwargs)-> Generator:
    debug = kwargs['debug']# kwargs.get('debug',Debug('validate_courses'))
    valid = []
    for i in data:
        _course_name = i['name']
        debug.print(f'\n### Started validating-> {_course_name}')
        # Check age. less than 3 days old is valid
        try:
            sale_start = arrow.get(i['sale_start'], 'ddd, DD MMM YYYY HH:mm:ss ZZZ')
            now = arrow.now(sale_start.tzinfo)
            days_diff_from_start = (sale_start.date() - now.date()).days
        except KeyError:
            debug.print("!! Skipped... Reason: No start date...")
            continue
       
        # Skip object more than 3 days old
        if days_diff_from_start > 3:
            debug.print('!! Skipped... Reason: More than 3 days old')
            continue

        # Skip if ended
        if i['sale_end'] != None:
            sale_end = arrow.get(i['sale_end'], 'ddd, DD MMM YYYY HH:mm:ss ZZZ') 
            days_diff_from_end = (sale_end.date() - now.date()).days
            if days_diff_from_end <= 0:
                debug.print('!! Skipped... Reason: Campaign Ended!')
                continue
        
        # Skip if expired
        if i['isexpired'] == 'Expired':
            debug.print('!! Skipped... Reason: Expired!')
            continue
        

        # Check if its actually free in Udemy. Skip is used or expired
        course_name,coupon_code = extractUdemyUrl(i['url'],debug=debug)
        if not course_name or not coupon_code:
            debug.print('!! Skipped... Reason: No coupon code found in the URL.')
            continue
        try:
            course_details, coupon_details = getUdemyData(course_name,coupon_code,fast,debug=debug)
        except TypeError:
            debug.print('!! Skipped... Reason: Unreachable url')
            continue

        try:
            amount = coupon_details['price_text']['data']['pricing_result']['price']['amount']
            original_price = coupon_details['price_text']['data']['pricing_result']['list_price']['amount']
        except KeyError:
            debug.print('!! Skipped... Reason: Course unavailable.')
            continue
        if not original_price: #if original price is $0
            debug.print('!! Skipped... Reason: listed for $0')
            continue
        if not amount: #if Free
            valid.append(_course_name)
            # valid.append({'details':course_details, 'coupon':coupon_details})
            debug.is_successful({"name":_course_name, "coupon":coupon_code})
            debug.print(f'$$$ Successful -> {_course_name}')
            yield {
                "url": f'https://www.udemy.com/course/{course_name}/?couponCode={coupon_code}',
                "course_id":course_details['id'],
                "title": course_details['title'],
                "coupon":coupon_code,
                "uses_remaining":coupon_details['price_text']['data']['pricing_result']['campaign']['uses_remaining'],
                "maximum_uses":coupon_details['price_text']['data']['pricing_result']['campaign']['maximum_uses'],
                "list_price":coupon_details['price_text']['data']['pricing_result']['list_price']['amount'],
                "amount":coupon_details['price_text']['data']['pricing_result']['price']['amount'],
                "currency_symbol":coupon_details['price_text']['data']['pricing_result']['price']['currency_symbol'],
            }
        else:
            debug.print('!! Skipped... Reason: Not free anymore.')
            continue

    debug.is_summary(f"\nTotal valid: {len(valid)}/{count}")
    debug.print(f"\nNice: {len(valid)}/{count} validated!")
    






