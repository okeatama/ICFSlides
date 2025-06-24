from datetime import datetime, timedelta
from pptx import Presentation
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import json
from constants import *

# Target website
BASE_URL = "https://www.lagumisa.web.id/lagumz.php?&f="



with open("JSON/calendar.json","r") as file:
    calendar = json.load(file)

with open("JSON/updated_mass_readings.json", "r") as file:
    mass_readings = json.load(file)

# gets date of next sunday
def get_next_sunday():
    today = datetime.now()
    days_ahead = (6 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7  # skip to next week if today is Sunday
    return today + timedelta(days=days_ahead)

def download_images_and_get_verse():
    # download responsorial psalm and gospel acclamation images
    
    mass_title_id = calendar[mass_date.month][mass_date.strftime("%Y-%m-%d")]

    for y in tries:
        url = f"{BASE_URL}{y}-{mass_title_id}"

        # try this url, and search for images in edisibaru
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        edisibaru = soup.find("div", id="edisibaru")

        if not edisibaru:
            continue

        # 1: since there is always an image before the 2 we want
        imgs = edisibaru.find_all("img")[1:]

        for i, img_tag in enumerate(imgs):
            img_url = urljoin(url, img_tag.get("src"))
            img_name = os.path.basename(img_url.split("?")[0])  # remove query params
            img_data = requests.get(img_url).content
            with open(f"images/{FILENAMES[i]}", "wb") as f:
                f.write(img_data)
            print(f"Downloaded {FILENAMES[i]}")

        presyair = edisibaru.find_all("pre", class_="presyair")[-1]
        return "\n".join(presyair.text.split('\n')[2:])

def create_reading_slide(prs, content, bible_loc, title):
    reading = prs.slides.add_slide(prs.slide_layouts[7])
    if len(content) > SLIDE_CONTENT_THRESHOLD:
        create_reading_slide(prs, content[SLIDE_CONTENT_THRESHOLD + 1:], bible_loc, title)
        content = content[:SLIDE_CONTENT_THRESHOLD + 1]
    reading.placeholders[10].text = content
    reading.placeholders[11].text = bible_loc
    reading.placeholders[12].text = title

def create_gospel_slide(prs, content, bible_loc):
    gospel = prs.slides.add_slide(prs.slide_layouts[10])
    if len(content) > SLIDE_CONTENT_THRESHOLD: 
        create_gospel_slide(prs, content[SLIDE_CONTENT_THRESHOLD + 1:], bible_loc)
        content = content[:SLIDE_CONTENT_THRESHOLD + 1]
    gospel.placeholders[10].text = content
    gospel.placeholders[11].text = bible_loc

def create_resp_psalm_slide(prs, bible_loc):
    responsorial_psalm = prs.slides.add_slide(prs.slide_layouts[8])
    responsorial_psalm.placeholders[11].text = bible_loc
    responsorial_psalm.placeholders[12].insert_picture(f"images/{FILENAMES[0]}")

def create_gospel_acclamation_slide(prs, verse):
    gospel_acclamation = prs.slides.add_slide(prs.slide_layouts[9])
    gospel_acclamation.placeholders[12].insert_picture(f"images/{FILENAMES[1]}")
    gospel_acclamation.placeholders[13].text = verse

# returns nothing, this use global var
def extract_mass_reading(mass_reading):
    first_readings = []
    first_verses = []
    second_readings = []
    second_verses = []
    gospel = []
    gospel_verses = []
    psalm_loc = ""

    for section in mass_reading:
        if section["header"] == "Reading 1":
            for r in section["readings"]:
                first_readings.append(r["text"])
                first_verses.append(r["verses"][0]["text"])
        
        elif section["header"] == "Reading 2":
            for r in section["readings"]:
                second_readings.append(r["text"])
                second_verses.append(r["verses"][0]["text"])
        elif section["header"] == "Responsorial Psalm":
            psalm_loc = section["readings"][0]["verses"][0]["text"]
        elif section["header"] == "Gospel":
            for r in section["readings"]:
                gospel.append(r["text"])
                gospel_verses.append(r["verses"][0]["text"])
    
    return (first_readings, first_verses, psalm_loc, second_readings, second_verses, gospel, gospel_verses)

mass_date = get_next_sunday()

verse = download_images_and_get_verse()
mass_reading = None

# find mass_reading for mass date
for i, r in enumerate(mass_readings):
    if r["date"] == mass_date.strftime("%Y-%m-%d"):
        mass_reading = mass_readings[i]["sections"]
        break

if not mass_reading:
    raise Exception(f"Couldn't find date {mass_date.strftime('%Y-%m-%d')}")

# now do some magic to extract readings, psalm and gospel
first_readings, first_verses, psalm_loc, second_readings, second_verses, gospel, gospel_verses = extract_mass_reading(mass_reading)

"""
pptx stuff
=============================================================
slide_layouts[7] is Readings
slide_layouts[8] is responsorial Psalm
slide_layouts[9] is Gospel Acclamation
slide_layouts[10] is Gospel

for slide_layouts[7] (Readings):
placeholders[10] is the actual reading
placeholders[11] is Book Chapter:verse
placeholders[12] is First Reading/Second Reading/Gospel

for slide_layouts[8] (responsorial Psalm):
placeholders[11] is Psalm Chapter:verse
placeholders[12] is the picture, use insert_picture("test.png")

for slide_layouts[9] (Gospel Acclamation):
placeholders[12] is the picture, use insert_picture("test.png")
placeholders[13] is the verse

for slide_layouts[10] (Gospel):
placeholders[10] is the actual reading
placeholders[11] is Book Chapter:verse

I estimate readings content only fit around 420-425 letters (including spaces)? Need to check more
"""
# create the presentation
prs = Presentation("template.pptx")
for i in range(len(first_readings)):
    create_reading_slide(prs, first_readings[i], first_verses[i], "First Reading")

create_resp_psalm_slide(prs, psalm_loc)

for i in range(len(second_readings)):
    create_reading_slide(prs, second_readings[i], second_verses[i], "Second Reading")

create_gospel_acclamation_slide(prs, verse)

for i in range(len(gospel)):
    create_gospel_slide(prs, gospel[i], gospel_verses[i])
pptxfilename = mass_date.strftime("%Y%m%d")
prs.save(f"{pptxfilename}.pptx")