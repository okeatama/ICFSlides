from datetime import datetime, timedelta
from pptx import Presentation
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import json
from constants import *
import csv

# Target website


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
        url = f"{LAGUMISA_BASE_URL}{y}-{mass_title_id}"

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

def extract_universalis():
    url = f'{UNIVERSALIS_BASE_URL}{mass_date.strftime("%Y%m%d")}/mass.htm'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    texts = soup.find("div", id="texts")
    content = texts.find("div").get_text()
    table = texts.find_all("th", align="right") # theres 5 usually, first verse, psalm, second, gospel acclamation, gospel

    # verses
    first_verse = table[0].get_text()
    psalm_loc = table[1].get_text()
    second_verse = table[2].get_text()
    gospel_verse = table[4].get_text()

    first_reading = ""
    second_reading = ""
    gospel = ""
    # signifies if they have collected first, second and gospel
    flags = [False, False, False] # first reading second reading, gospel

    line_iter = iter(content.split('\n'))
    sentinel = object()
    while True:
        line = next(line_iter, sentinel)
        if line is sentinel:
            # out of iteration
            break

        if "First reading" in line and not flags[0]:
            readings = [] # array of strings of line of verses
            while True:
                next_line = next(line_iter, sentinel)
                if (next_line is sentinel) or next_line.strip().startswith("How to listen"):
                    # break out of the iteration
                    break
                readings.append(next_line.strip())
            
            first_reading = "\n".join(readings)
            flags[0] = True
        elif "Second reading" in line and not flags[1]:
            readings = []
            while True:
                next_line = next(line_iter, sentinel)
                if (next_line is sentinel) or next_line.strip().startswith("Gospel Acclamation"):
                    # break out of the iteration
                    break
                readings.append(next_line.strip())
            second_reading = "\n".join(readings)
            flags[1] = True
        elif "Gospel Acclamation" in line:
            # skip over Gospel Acclamation, since this word contains "Gospel"
            continue
        elif "Gospel" in line and not flags[2]:
            readings = []
            while True:
                next_line = next(line_iter, sentinel)
                if (next_line is sentinel) or next_line.strip().startswith("The responsorial psalms"):
                    # break out of the iteration
                    break
                readings.append(next_line.strip())
            gospel = "\n".join(readings)
            flags[2] = True
        
        if all(flags):
            # all three has been extracted, no need to go any further
            break
    
    return (first_reading, first_verse, psalm_loc, second_reading, second_verse, gospel, gospel_verse)

def create_birthday_slide(prs):
    with open("data.csv", "r", encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        durs = [timedelta(days=i) for i in range(7)]
        # dur = timedelta(days=6)
        from_date = mass_date - timedelta(days=6)

        # acceptable values
        # date_range = [str(i) for i in range(from_date.day, mass_date.day + 1)]
        date_range = {str((mass_date - dur).day) for dur in durs}
        month_range = set()
        month_range.add(str(from_date.month))
        month_range.add(str(mass_date.month))

        acceptable_active = ["Active", "Not Sure"]

        lines = []

        for row in csv_reader:
            if row["Month"] in month_range and row["Date"] in date_range and row["Active"] in acceptable_active:
                # birthday in range
                full_name = f"{row['First Name']} {row['Middle Name']} {row['Last Name']}"
                line = f"{row['Date']} {NUM_TO_MONTH_ID[int(row['Month'])]}: {full_name}"
                lines.append(line)
    
    bday = prs.slides.add_slide(prs.slide_layouts[11])
    final_text = f"Bagi Mereka yang berulang tahun pada, {from_date.day} - {mass_date.day} {NUM_TO_MONTH_ID[mass_date.month]}:"
    final_text = final_text + '\n\n' + '\n'.join(lines)
    bday.placeholders[10].text = final_text

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
# first_readings, first_verses, psalm_loc, second_readings, second_verses, gospel, gospel_verses = extract_mass_reading(mass_reading)
first_reading, first_verse, psalm_loc, second_reading, second_verse, gospel, gospel_verse = extract_universalis()

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
create_birthday_slide(prs)
create_reading_slide(prs, first_reading, first_verse, "First Reading")

create_resp_psalm_slide(prs, psalm_loc)

create_reading_slide(prs, second_reading, second_verse, "Second Reading")

create_gospel_acclamation_slide(prs, verse)

create_gospel_slide(prs, gospel, gospel_verse)
pptxfilename = mass_date.strftime("%Y%m%d")
prs.save(f"{pptxfilename}.pptx")