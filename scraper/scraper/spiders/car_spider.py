import requests
import scrapy

cities = {
    'tehran': 1,
    'karaj': 2,
    'isfahan': 4,
    'tabriz': 5,
    'urmia': 10,
    'rasht': 12,
    'sari': 22,
    'sanandaj': 28,
}


def get_first_page_last_post_date():
    post_list_url = 'https://api.divar.ir/v8/web-search/tehran/car'
    payload={}
    headers = {
    'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://divar.ir/',
    'sec-ch-ua-mobile': '?1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
    'sec-ch-ua-platform': '"Android"',
    'Cookie': 'did=d2a18e44-1f64-4c2b-98f6-feacc0ff80bf'
    }

    response = requests.request("GET", post_list_url, headers=headers, data=payload, timeout=5)
    return response.json().get('last_post_date')




def get_tokens(last_post_date, city_number, post_category='light', pages_to_crawl=2):

    post_list_url = f'https://api.divar.ir/v8/web-search/{city_number}/{post_category}'

    headers = {
        'Content-Type': 'application/json'
    }

    list_of_tokens = []
    for _ in range(pages_to_crawl):
        json = {
            "json_schema": 
            {
                "category": {"value": post_category}
            },
            "last-post-date": last_post_date
        }
        res = requests.post(post_list_url, json=json, headers=headers, timeout=5)
        data = res.json()
        last_post_date = data['last_post_date']

        for widget in data['web_widgets']['post_list']:
            token = widget['data']['token']
            list_of_tokens.append(token)

    return list_of_tokens


class CarPostsSpider(scrapy.Spider):
    name = 'divar'

    tokens_list = get_tokens(
        last_post_date=get_first_page_last_post_date(),
        city_number=cities['tehran'],
        pages_to_crawl=19
        )
    tokens_list = ['QZJ8laFv']
    start_urls = [f'https://divar.ir/v/-/{token}' for token in tokens_list]

    def parse(self, response, **kwargs):
        informations = response.css('div span.kt-group-row-item__value::text')
        # print(informations[0].extract())
        print('kire khar')
        # area = int(informations[0].extract())
        # construction = int(informations[1].extract())
        # rooms = int(informations[2].extract())

        # warehouse = False if 'ندارد' in informations[3].extract() else True
        # parking = False if 'ندارد' in informations[4].extract() else True
        # elevator = False if 'ندارد' in informations[5].extract() else True

        address = response.css('div div.kt-page-title__subtitle--responsive-sized::text').extract()
        # price = response.css('div p.kt-unexpandable-row__value::text').extract_first()

        description = response.css('div p.kt-description-row__text--primary').extract_first()

        yield {
            'Address': address,
            'Description': description
        }
