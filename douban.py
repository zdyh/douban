#!/usr/bin/env python3

import json
import re
from urllib.parse import urljoin, urlsplit

import argh
import requests
from bs4 import BeautifulSoup

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ja,zh-CN;q=0.8,en-US;q=0.5,en;q=0.3',
}

cookies = {
    'gr_user_id': 'you gr_user_id in cookies',
}

douban_book_url = {
    'watching': 'https://book.douban.com/people/{0}/do',
    'watched': 'https://book.douban.com/people/{0}/collect',
    'want': 'https://book.douban.com/people/{0}/wish',
}

douban_movie_url = {
    'see': 'https://movie.douban.com/people/{0}/do',
    'read': 'https://movie.douban.com/people/{0}/collect',
    'want': 'https://movie.douban.com/people/{0}/wish',
}


def get_text(tag):
    if isinstance(tag, list):
        if len(tag):
            tag = tag[0]
        else:
            return ''
    return re.sub(r'\s+', ' ', tag.get_text().strip())


def get_douban(base_url):
    def get(url):
        return session.get(url, headers=headers, cookies=cookies)

    with requests.session() as session:
        parts = urlsplit(base_url)
        headers['host'] = parts.netloc
        headers['referer'] = parts._replace(path='/mine').geturl()

        link = base_url

        while link:
            r = get(link)
            if r.ok:
                soap = BeautifulSoup(r.text, 'lxml')
                yield soap
            try:
                link = next(next_page(base_url, soap))
            except StopIteration:
                return


def next_page(base_url, doc):
    for page in doc.select('.paginator > .next'):
        for link in page.find_all('a', href=True):
            yield urljoin(base_url, link['href'])


def get_book_info(doc):
    for data in doc.select('.interest-list > .subject-item'):
        book = dict()
        book['link'] = data.select('h2 > a')[0]['href']
        book['title'] = get_text(data.find('h2'))
        book['cover'] = data.select('.pic > .nbg > img')[0]['src']

        pub_info = get_text(data.select('.info > .pub'))
        book['pub'] = pub_info.strip()
        # book['translator'] = pub_info[1].strip() if len(pub_info) > 4 else ''
        # book['price'] = pub_info[-1].strip() if len(pub_info) >= 2 else ''
        # book['publish_date'] = pub_info[-2].strip() if len(pub_info) >= 3 else ''
        # book['press'] = pub_info[-3].strip() if len(pub_info) >= 4 else ''

        status = get_text(data.select('.short-note .date')).split(' ')
        book['updation'] = status[0]
        book['status'] = status[1]

        labels = get_text(data.select('.short-note .tags'))
        book['labels'] = labels.replace('标签: ', '').split(' ')
        yield book


@argh.named('book')
def get_my_books(user_id):
    def my_book():
        for _, url in douban_book_url.items():
            for doc in get_douban(url.format(user_id)):
                yield from get_book_info(doc)

    print(json.dumps(list(my_book()), indent=4, ensure_ascii=False))


def get_movie_info(doc):
    movies = doc.select('.grid-view')[0]
    for data in movies.find_all('div', {'class': 'item'}):
        movie = dict()

        info = data.select('.info > ul > li')
        title = info[0].a
        movie['link'] = title['href']
        movie['title'] = get_text(title)

        for span in info[2].select('span'):
            glass = span['class'][0]
            if 'date' == glass:
                movie['updation'] = get_text(span)
            elif glass.startswith('rating'):
                movie['rating'] = re.search(r'\d+', glass).group()

        labels = get_text(data.select('.tags'))
        movie['labels'] = labels.replace('标签: ', '').split(' ')

        movie['cover'] = data.select('.pic > .nbg > img')[0]['src']
        movie['info'] = get_text(info[1])

        yield movie


@argh.named('movie')
def get_my_movies(user_id):
    def my_movies():
        for _, url in douban_movie_url.items():
            for doc in get_douban(url.format(user_id)):
                yield from get_movie_info(doc)

    print(json.dumps(list(my_movies()), indent=4, ensure_ascii=False))


if __name__ == '__main__':
    parser = argh.ArghParser()
    parser.add_commands([get_my_books, get_my_movies])
    parser.dispatch()
