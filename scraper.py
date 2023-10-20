import json
import time

import requests

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

request_headers = {
    'authority': 'api.divar.ir',
    'accept': 'application/json-filled',
    'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
    'origin': 'https://divar.ir',
    'referer': 'https://divar.ir/',
    'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Cookie': 'did=d2a18e44-1f64-4c2b-98f6-feacc0ff80bf'
}


def get_first_page_last_post_date():
    post_list_url = 'https://api.divar.ir/v8/web-search/tehran/car'
    payload = {}

    response = requests.get(
        post_list_url, headers=request_headers, data=payload, timeout=5)
    return response.json().get('last_post_date')


def get_tokens(last_post_date, city_number, post_category='light', pages_to_crawl=20):

    post_list_url = f'https://api.divar.ir/v8/web-search/{city_number}/{post_category}'

    list_of_tokens = []
    for _ in range(pages_to_crawl):
        json = {
            "json_schema":
            {
                "category": {"value": post_category}
            },
            "last-post-date": last_post_date
        }
        res = requests.post(post_list_url, json=json, headers=request_headers, timeout=5)
        data = res.json()
        last_post_date = data['last_post_date']

        for widget in data['web_widgets']['post_list']:
            token = widget['data']['token']
            list_of_tokens.append(token)

    return list_of_tokens


def crawl_post_detail_page(city_slug, city_id):

    tokens_list = get_tokens(
        last_post_date=get_first_page_last_post_date(),
        city_number=city_id,
        pages_to_crawl=20
    )

    print(tokens_list)

    posts_datas = []
    for token in tokens_list:
        time.sleep(1)
        post_url = f'https://api.divar.ir/v8/posts-v2/web/{token}'
        res = requests.get(post_url, headers=request_headers, timeout=7)
        data = res.json().get('sections')
        post_data = {}
        for item in data:
            if item.get('section_name') == 'TITLE':
                post_data['title'] = item['widgets'][0]['data']['title']
                post_data['subtitle'] = item['widgets'][0]['data']['subtitle']
            elif item.get('section_name') == 'DESCRIPTION':
                post_data['description'] = item['widgets'][1]['data']['text']
            elif item.get('section_name') == 'LIST_DATA':
                post_data['milage'] = item['widgets'][0]['data']['items'][0]['value']
                post_data['model'] = item['widgets'][0]['data']['items'][1]['value']
                post_data['color'] = item['widgets'][0]['data']['items'][2]['value']
        posts_datas.append(post_data)

    with open(f'{city_slug}_car_datas.json', 'w', encoding='utf-8') as f:
        json.dump(posts_datas, f, indent=4)

if __name__ == '__main__':
    for key, value in cities.items():
        print(key, value)
        crawl_post_detail_page(city_slug=key, city_id=cities[key])
