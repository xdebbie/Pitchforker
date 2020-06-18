from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import sys
import sqlite3
from peewee import IntegrityError
from htmldate import find_date
from models import Pitchfork


sess = HTMLSession()
# touching recursion_depth will lead to generating duplicates - leave it as "1"
RECURSION_DEPTH = 1
# max_workers defines how many workers will be running the script in parallel. The higher is the number, the most resources it will consume and the faster the script will run
MAX_WORKERS = 70


def scrape_urls(url):
    if isinstance(url, list):
        # in this case, flatten
        links = []
        for u in url:
            links += list(scrape_urls(u))
        return filter(lambda x: "/reviews/albums" in x and "?" not in x, links)
    resp = sess.get(url)
    links = resp.html.absolute_links
    return filter(lambda x: "/reviews/albums" in x and "?" not in x, links)


def scrape_page(url, recur_depth=0):
    # url
    data = {'url': url}
    resp = sess.get(url)
    # publication date of the review
    pubdate = find_date(url)
    if pubdate:
        data['pubdate'] = pubdate
    # score by pitchfork
    score = resp.html.find('.score')
    if score:
        data['score'] = score[0].text
    # album year
    year = resp.html.find('.single-album-tombstone__meta-year')[0].text
    if year:
        data['year'] = year.strip('•')
    # record label
    label = resp.html.find('.labels-list__item')
    if label:
        data['label'] = label[0].text
    # genre
    genre = resp.html.find('.genre-list__link')
    if genre:
        data['genre'] = genre[0].text
    # artwork
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'html.parser')
    div = soup.find('div', {'class': 'single-album-tombstone__art'})
    data['artwork'] = div.find('img')['src']
    # review title
    title = resp.html.find('title')[0].text
    data['title'] = title
    if title:
        try:
            # artist
            data['artist'] = title.split(":")[0]
            # album title
            data['album'] = title[title.index(
                ":")+1:title.index("Album Review")].strip()
        except ValueError:
            return
    yield (data)

    if recur_depth > 0:
        links = filter(lambda x: "/reviews/albums/?page=" in x and "?" not in x,
                       resp.html.absolute_links)
        for link in links:
            for page in scrape_page(link, recur_depth=recur_depth - 1):
                yield(page)


def insert_review(data):
    new_review = Pitchfork(artist=data['artist'], album=data['album'])
    try:
        new_review.title = data['title']
    except KeyError:
        pass
    try:
        new_review.score = data['score']
    except KeyError:
        pass
    try:
        new_review.year = data['year']
    except KeyError:
        pass
    try:
        new_review.label = data['label']
    except KeyError:
        pass
    try:
        new_review.genre = data['genre']
    except KeyError:
        pass
    try:
        new_review.url = data['url']
    except KeyError:
        pass
    try:
        new_review.pubdate = data['pubdate']
    except KeyError:
        pass
    try:
        new_review.artwork = data['artwork']
    except KeyError:
        pass
    new_review.save()


def mine_page(url, recur_depth=RECURSION_DEPTH):
    'scrapes page and inserts into db, designed to be used with ThreadPoolExecutor'
    for data in scrape_page(url, recur_depth=recur_depth):
        try:
            insert_review(data)
        except IntegrityError:
            pass


if __name__ == "__main__":
    # there are 1,876 album pages currently on pitchfork. The default link will make the iteration from the ?page=1 to the ?page=x
    default_link = 'https://pitchfork.com/reviews/albums/?page='
    try:
        if "pitchfork.com" in sys.argv[1]:
            link = sys.argv[1]
        elif all(map(lambda x: x.isdigit(), sys.argv[1])):
            # the iteration, from 1 to x in range
            link = [default_link + str(i) for i in range(int(sys.argv[1]))]
    except IndexError:
        # if your computer cannot handle in a single run the range of 1 to 1,876, it is recommended to run the script 4 times: from 1 to 501, 501 to 1001, 1001 to 1501 and 1501 to 1,876 (or whatever the last page currently is)
        link = [default_link + str(i) for i in range(1, 7)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as exc:
        scraper = {exc.submit(mine_page, url): url for url in scrape_urls(link)}
        for future in concurrent.futures.as_completed(scraper):
            print(scraper[future])

# finding and deleting duplicates on the database using sqlite3
# connecting to the database
connection = sqlite3.connect("albums.db")
# cursor
crsr = connection.cursor()

# SLQ command
sql_command = """DELETE FROM pitchfork
WHERE id IN
    (SELECT id
    FROM 
        (SELECT id,
         ROW_NUMBER() OVER( PARTITION BY url
        ORDER BY  id ) AS row_num
        FROM pitchfork ) t
        WHERE t.row_num > 1 );"""
# execute the statement
crsr.execute(sql_command)

# commit changes
connection.commit()
# close the connection
connection.close()