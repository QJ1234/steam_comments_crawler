import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urljoin
import pandas as pd
import re
from tqdm import tqdm
from urllib3.exceptions import InsecureRequestWarning
import json

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def parse_reviews(review):
    card = review.find('div', {'class': 'apphub_CardTextContent'})
    date_posted = card.find('div', {'class': 'date_posted'})
    date_posted.decompose()
    text = re.sub(r'[\n\t\xa0]', '', card.text)
    return text

def get_reviews_per_page(url, headers):
    html = requests.get(url, headers=headers, timeout=5, verify=False)
    soup = BeautifulSoup(html.text, 'html.parser')
    reviews = soup.find_all('div', {'class': 'apphub_Card'})
    review_list = []
    user_reviews_cursor = soup.find('input', {'name': 'userreviewscursor'})['value']
    for review in reviews:
        nick = review.find('div', {'class': 'apphub_CardContentAuthorName'})
        title = review.find('div', {'class': 'title'}).text
        hours = review.find('div', {'class': 'hours'}).text.split(' ')
        date_posted = review.find('div', {'class': 'date_posted'}).text
        num_replys = review.find('div', {'class': 'apphub_CardCommentCount alignNews'}).text.replace(',', '')
        content_text = parse_reviews(review)
        cell = [nick.text, title, hours, date_posted, num_replys, content_text, user_reviews_cursor]
        review_list.append(cell)
    
    return review_list, user_reviews_cursor
    
def get_url(game_id, i, language, user_reviews_cursor):
    if i == 2:
        query_params = {
            'userreviewscursor': user_reviews_cursor,
            'userreviewsoffset': str(10 * (i - 1)),
            'p': str(i),
            'workshopitemspage': str(i),
            'readytouseitemspage': str(i),
            'mtxitemspage': str(i),
            'itemspage': str(i),
            'screenshotspage': str(i),
            'videospage': str(i),
            'artpage': str(i),
            'allguidepage': str(i),
            'webguidepage': str(i),
            'integratedguidepage': str(i),
            'discussionspage': str(i),
            'numperpage': '10',
            'browsefilter': 'mostrecent',
            'browsefilter': 'mostrecent',
            'l': language,
            'appHubSubSection': '10',
            'filterLanguage': language,
            'searchText': '',
            'maxInappropriateScore': '100',
            'forceanon': '1'}
    else:
        query_params = {
            'userreviewscursor': user_reviews_cursor,
            'userreviewsoffset': str(10 * (i - 1)),
            'p': str(i),
            'workshopitemspage': str(i),
            'readytouseitemspage': str(i),
            'mtxitemspage': str(i),
            'itemspage': str(i),
            'screenshotspage': str(i),
            'videospage': str(i),
            'artpage': str(i),
            'allguidepage': str(i),
            'webguidepage': str(i),
            'integratedguidepage': str(i),
            'discussionspage': str(i),
            'numperpage': '10',
            'browsefilter': 'mostrecent',
            'browsefilter': 'mostrecent',
            'l': language,
            'appHubSubSection': '10',
            'appHubSubSection': '10',
            'filterLanguage': language,
            'searchText': '',
            'maxInappropriateScore': '100',
            'forceanon': '1'}
        
    base_url = 'http://steamcommunity.com/app/'
    url = urljoin(base_url, f'{game_id}/homecontent/') + '?' + urlencode(query_params)    
    return url


def crawl(url, game_id, num_comments, language, file_name, headers):
    num_pages = (num_comments + 9) // 10 
    columns = ['nick', 'title', 'hour', 'date_posted', 'num_replys', 'content_text', 'user_reviews_cursor']

    if os.path.exists(file_name):
        reviews_past = pd.read_csv(file_name, encoding='utf-8')
        user_reviews_cursor = reviews_past['user_reviews_cursor'].iloc[-1]
        current_page = ((reviews_past.shape[0] + 9) // 10) + 1
        print("find breakpoint, continue crawling from page", current_page)
    else:
        first_page_list, user_reviews_cursor = get_reviews_per_page(url, headers=headers)
        first_page_df = pd.DataFrame(first_page_list, columns=columns)
        first_page_df.to_csv(file_name, encoding='utf-8', index=False)
        current_page = 2
    with tqdm(total=num_pages - current_page + 1) as pbar:    
        for i in range(current_page, num_pages + 1):
            url = get_url(game_id, i, language, user_reviews_cursor)
            review_list, user_reviews_cursor = get_reviews_per_page(url, headers=headers)
            df = pd.DataFrame(review_list, columns=columns)
            df.to_csv(file_name, encoding='utf-8', mode='a', header=False, index=False)
            pbar.set_description(f'crawling page {i}')
            pbar.update(1)
        current_page = i
        return current_page

with open('configs.json', 'r') as f:
    configs = json.load(f)

url = configs.get('url')
game_id = configs.get('game_id')
num_comments = configs.get('num_comments')
language = configs.get('language')
file_name = configs.get('file_name')
headers = configs.get('headers')


def main():
    with open('configs.json', 'r') as f:
        configs = json.load(f)

    url = configs.get('url')
    game_id = configs.get('game_id')
    num_comments = configs.get('num_comments')
    language = configs.get('language')
    file_name = configs.get('file_name')
    headers = configs.get('headers')
    while True:
        try:
            current_page = crawl(url, game_id, num_comments, language, file_name, headers)
            if current_page == (num_comments + 9) // 10:
                break
        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    main()
