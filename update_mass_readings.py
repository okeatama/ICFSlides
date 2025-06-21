from tutorial.declarations import books, catholic_bible_chapters
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

with open("mass_readings.json", "r") as file:
    data = json.load(file)

base_url = "https://www.catholic.org/bible/book.php"