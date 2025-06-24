# ICFSlides
Web scraper to automate mass slides

Included is scraped bible (New Jerusalem Bible) from https://www.catholic.org/bible/book.php, can be found in bible/bible.json. 0.json - 72.json are each books in the bible. To access the bible's verses, use python

```
import json
from tutotial.bible_chapters import books

with open("bible/bible.json", "r") as file:
    bible = json.load(file)
book_name = "Genesis" # change to whatever the name of the book is
book_number = books.index(book_name)
chapter = 1

# programmer indexing vs normal people indexing
verse_start = 1 - 1 # always minus 1
verse_end = 10 - 1 # always minus 1
verse = 5 - 1 # always minus 1

bible[book_number][chapter][verse_start:verse_end]
bible[book_number][chapter][verse]
```

To scrape:
```
scrapy crawl <crawler name> -O <output.json> [-a <param=val>]
```

A batch file, `tutorial/run_crawler.py` shows how the crawlers are used.

To compile all the books copy the 0.json to 72.json to bible folder, then run create_bible.py `py ./create_bible.py`, which results in bible/bible.json

To get sunday mass readings, run `./gen_readings.bat` or lookup `python catholic mass readings`. This will output JSON/mass_readings.json.

ICF uses Universalis, which I believe use NJB, but `JSON/mass_readings.json` uses another version, so `update_mass_reading.py` will update it to use NJB. Need to change `JSON/mass_readings.json` a bit, if there are any "or" readings (even though they already have 2 different readings, they didn't need the or), remove them and replace accordingly. This creates another JSON file `updated_mass_readings.json` (remember to put JSON file in JSON folder)

Next is the calendar, which I need for https://www.lagumisa.web.id/mazmur.php to get responsorial psalm, gospel acclamation and its verse. I'm scraping it from https://www.imankatolik.or.id/kalender.php. Therefore, another scraper is used (named calendar). Check content of `run_crawler.bat` on how to run. The result is a JSON file called calendar.json, which is then cleaned by running `edit_calendar.py` (same as above, put JSON in JSON folder)

Finally, with some magic from `python-pptx` library, `generate_slide.py` will create a pptx file named after the date of next sunday mass (i.e. 20250629), with all the readings, gospel, responsorial psalm and gospel acclamation in it. Need to check if content is in the boundary of slides, since newlines cause lots of problems.