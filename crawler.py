import json
import os
import random
import re
import time
from typing import List, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests import Session
from tqdm import tqdm
from urllib.parse import urlencode, urljoin
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def _clean_text(value: str) -> str:
    return re.sub(r'[\n\t\xa0]', '', value)


def parse_reviews(review) -> str:
    card = review.select_one('.apphub_CardTextContent')
    if not card:
        return ''
    date_posted = card.select_one('.date_posted')
    if date_posted:
        date_posted.decompose()
    return _clean_text(card.text)


def build_url(game_id: str, page: int, language: str, user_reviews_cursor: str) -> str:
    query_params = {
        'userreviewscursor': user_reviews_cursor,
        'userreviewsoffset': str(10 * (page - 1)),
        'p': str(page),
        'workshopitemspage': str(page),
        'readytouseitemspage': str(page),
        'mtxitemspage': str(page),
        'itemspage': str(page),
        'screenshotspage': str(page),
        'videospage': str(page),
        'artpage': str(page),
        'allguidepage': str(page),
        'webguidepage': str(page),
        'integratedguidepage': str(page),
        'discussionspage': str(page),
        'numperpage': '10',
        'browsefilter': 'mostrecent',
        'browsefilter': 'mostrecent',
        'appid': game_id,
        'appHubSubSection': '10',
        'appHubSubSection': '10',
        'l': language,
        'filterLanguage': language,
        'searchText': '',
        'maxInappropriateScore': '100',
    }
    base_url = 'http://steamcommunity.com/app/'
    return urljoin(base_url, f'{game_id}/homecontent/') + '?' + urlencode(query_params)


def get_reviews_per_page(session: Session, url: str, max_retries: int = 3, backoff: float = 1.5) -> Tuple[List[List[str]], str]:
    last_exc = None
    for attempt in range(max_retries):
        try:
            html = session.get(url, timeout=5, verify=False)
            html.raise_for_status()
            soup = BeautifulSoup(html.text, 'lxml')
            cursor_tag = soup.select_one('input[name="userreviewscursor"]')
            if not cursor_tag or not cursor_tag.has_attr('value'):
                raise ValueError('missing userreviewscursor')
            user_reviews_cursor = cursor_tag['value']
            reviews = soup.select('.apphub_Card.modalContentLink.interactable')
            review_list = []
            for review in reviews:
                nick = review.select_one('.apphub_CardContentAuthorName')
                title = review.select_one('.title')
                hours = review.select_one('.hours')
                date_posted = review.select_one('.date_posted')
                num_replys = review.select_one('.apphub_CardCommentCount.alignNews')
                find_helpful = review.select_one('.found_helpful')
                awarded = review.select_one('.review_award_aggregated.tooltip')
                num_user_products = review.select_one('.apphub_CardContentMoreLink.ellipsis')
                content_text = parse_reviews(review)
                cell = [
                    nick.text.strip() if nick else '',
                    title.text.strip() if title else '',
                    hours.text.strip().split(' ') if hours else [],
                    date_posted.text.strip() if date_posted else '',
                    (num_replys.text.replace(',', '').strip() if num_replys else ''),
                    find_helpful.text.strip() if find_helpful else '',
                    awarded.text.strip() if awarded else '',
                    num_user_products.text.strip() if num_user_products else '',
                    content_text,
                    user_reviews_cursor
                ]
                review_list.append(cell)
            return review_list, user_reviews_cursor
        except Exception as exc:
            last_exc = exc
            time.sleep(backoff * (1 + random.random()))
    raise last_exc


def crawl(session: Session, url: str, game_id: str, num_comments: int, language: str, file_name: str) -> int:
    num_pages = (num_comments + 9) // 10
    columns = ['nick', 'title', 'hour', 'date_posted', 'num_replys', 'find_helpful', 'awarded', 'num_user_products', 'content_text', 'user_reviews_cursor']
    buffer: List[List[str]] = []
    rows_per_flush = 200

    def flush_buffer(header: bool = False):
        if not buffer:
            return
        pd.DataFrame(buffer, columns=columns).to_csv(
            file_name,
            encoding='utf-8-sig',
            mode='a',
            header=header,
            index=False
        )
        buffer.clear()

    if os.path.exists(file_name):
        reviews_past = pd.read_csv(file_name, encoding='utf-8')
        user_reviews_cursor = reviews_past['user_reviews_cursor'].iloc[-1]
        current_page = ((reviews_past.shape[0] + 9) // 10) + 1
        print('find breakpoint, continue crawling from page', current_page)
        header_needed = False
    else:
        first_page_list, user_reviews_cursor = get_reviews_per_page(session, url)
        buffer.extend(first_page_list)
        flush_buffer(header=True)
        current_page = 2
        header_needed = False

    if current_page > num_pages:
        return num_pages

    with tqdm(total=num_pages - current_page + 1) as pbar:
        for i in range(current_page, num_pages + 1):
            page_url = build_url(game_id, i, language, user_reviews_cursor)
            review_list, user_reviews_cursor = get_reviews_per_page(session, page_url)
            buffer.extend(review_list)
            if len(buffer) >= rows_per_flush:
                flush_buffer(header=header_needed)
                header_needed = False
            pbar.set_description(f'crawling page {i}')
            pbar.update(1)
        flush_buffer(header=header_needed)
        return i


def main():
    with open('configs.json', 'r') as f:
        configs = json.load(f)

    url = configs.get('url')
    game_id = configs.get('game_id')
    num_comments = configs.get('num_comments')
    language = configs.get('language')
    file_name = configs.get('file_name')
    headers = configs.get('headers') or {}

    with requests.Session() as session:
        session.headers.update(headers)
        while True:
            try:
                current_page = crawl(session, url, game_id, num_comments, language, file_name)
                if current_page == (num_comments + 9) // 10:
                    break
            except requests.RequestException as exc:
                print('network error, backing off:', exc)
                time.sleep(random.uniform(5, 12))
            except Exception as exc:
                print('unexpected error, backing off:', exc)
                time.sleep(random.uniform(15, 25))


if __name__ == '__main__':
    main()