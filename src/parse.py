import re
import urllib.request
import os.path
from datetime import date
import datetime


# TODO:
#   - [x] Support parsing the year in which the book was read
#   - [x] Skip section of READING: now showing it tagged
#   - [x] Remove "copy" link: change for "summary" if we have it
#   - [x] Add the score of the books
#   - [x] When clicking on the page, go to it's associated link (goodreads)
#   - [ ] Remove "burger popup" on the main menu
#   - [ ] Commit all of this, and configure pieline to build the site on every commit
#   - [ ] Remove previously generated files before generate the new ones

bookRe = re.compile(r"^[^[]*[^[]*\[(?P<name>[^]]+)\]\((?P<url>[^)]+)\) by _(?P<author>.*)_")
scoreRe = re.compile(r"(?P<score>\d+)\/10")
goodreadsImageRe = re.compile(r'coverImage.*src="(?P<image>[^"]+)')


FILENAME = "../README.md"
DEFAULT_BOOK_IMAGE = "example.jpeg"


def readFile(f):
    with open(f, encoding='utf8') as f:
        return f.read()

def parse_line(line):
    if not line.startswith("1. ") or not line.strip():
        return

    line = line.strip()

    r = bookRe.match(line)
    if not r or not r.groupdict():
        print("Error parsing line: ", line)
        return

    book = r.groupdict()
    book['audiobook'] = 'audiobook' in line

    score = scoreRe.search(line)
    if score:
        book.update(score.groupdict())

    return book

def parse(data):
    books = []
    group = ""
    for line in data.split('\n'):
        if line.startswith("# "):
            group = line.strip()[2:]
        book = parse_line(line)
        if book:
            book['group'] = group
            books.append(book)
    return books

def book_image_path(book):
    return './books/static/images/' + book_image_url(book)

def book_image_url(book):
    return 'books/' + book['name'] + ".jpg"

def download_image(img_url, book):
    try:
        response = urllib.request.urlopen(img_url)
        data = response.read()
    except Exception:
        print("[Error] Unable to download image for:", book['name'])
        return
    with open(book_image_path(book), 'wb') as f:
        f.write(data)

def search_image(book):
    book['image'] = DEFAULT_BOOK_IMAGE

    if not "goodreads.com" in book.get('url'):
        print("Unknown URL", book['name'], book['url'])
        return

    if os.path.isfile(book_image_path(book)):
        book['image'] = book_image_url(book)
        return

    print ("[INFO] Image not found for:", book['name'])

    try:
        html = readURL(book.get('url'))
    except:
        print("[Error] Unable to download image for:", book['name'])
        return

    image = goodreadsImageRe.search(html)
    if image and image.groupdict() and image.groupdict().get('image'):
        img_url = image.groupdict().get('image')
        download_image(img_url, book)
        book['image'] = book_image_url(book)

def search_all_images(books):
    for book in books:
        search_image(book)

def create_all_pages(tpl, books):
    for book in books:
        #print("Creating page for:", book.get('name'))
        create_page(tpl, book)

def create_page(tpl, book):
    tpl = tpl.replace("NAME", book.get('name'))

    tags = []
    if book.get('audiobook'):
        tags.append('audiobook')

    if book.get('score'):
        tags.append(book['score'] + "/10")
    if book.get('group'):
        tags.append(book['group'])

    tpl = tpl.replace("TAGS", ", ".join(tags))
    tpl = tpl.replace("IMAGE", book.get('image', DEFAULT_BOOK_IMAGE))
    tpl = tpl.replace("DATE", book.get('read_at'))
    tpl = tpl.replace("URL", book.get('url'))
    writeFile(tpl, "./books/content/" + book.get('name') + ".md")

def writeFile(data, path):
    with open(path, 'w') as f:
        f.write(data)

def readURL(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    return text

def add_dates(books):
    # We'll fake the dates, since I don't know the read_at, really.
    # It should be done even by year, but I'm not even going to do it like
    # this, yet
    today = date.today()
    for book in books:
        book['read_at'] = today.strftime("%Y-%m-%d")
        today = today - datetime.timedelta(1)
    return books


books = add_dates(parse(readFile(FILENAME)))
print("[INFO] Books read: ", len(books))
tpl = readFile("template.md")
search_all_images(books)
create_all_pages(tpl, books)
print("[INFO] Done")
