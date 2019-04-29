from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.request import Request
from bs4 import BeautifulSoup
from random import randint
from os import rename
import os
from io import StringIO
import gzip
import logging
import json
import time


def generate_url(n):
    return "https://www.ultimate-guitar.com/explore?page=" + str(n) + "&part[]=solo"


def get_solo_urls(text):
    d = json.loads(text.split("window.UGAPP.store.page")[-1].split(";")[0][2:])
    solo_urls = []
    try:
        tabs = d["data"]["data"]["tabs"]
        for tab in tabs:
            try:
                solo_url = tab["tab_url"]
                solo_urls.append(solo_url)
            except:
                pass
        return solo_urls
    except:
        return []


def scrape(list_pages_folder, solo_pages_folder):
    for i in range(1, 21):
        url = generate_url(i)
        try:
            page = urlopen(url)
            soup = BeautifulSoup(page, "html.parser")
            name = "page_" + str(i) + ".html"
            with open(os.path.join(list_pages_folder, name), "w+") as f:
                f.write(str(soup))
            solo_urls = get_solo_urls(str(soup))
            for solo_url in solo_urls:
                print(solo_url)
                page = urlopen(solo_url)
                soup = BeautifulSoup(page, "html.parser")
                name = solo_url.split('/')[-1] + ".html"
                with open(os.path.join(solo_pages_folder, name), "w+") as f:
                    f.write(str(soup))
                logging.info("Saved tab {0}".format(name))
            time.sleep(0.1)
        except:
            pass
