# ICFSlides
Web scraper to automate mass slides

Included is scraped bible (New Jerusalem Bible) from https://www.catholic.org/bible/book.php, can be found in bible/bible.json. 0.json - 72.json are each books in the bible. To access the bible's verses, use python

```
import json
from tutotial.declarations import books

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
cd tutorial
./run_crawler.bat
```

To compile all the books copy the 0.json to 72.json to bible folder, then run create_bible.py `py ./create_bible.py`

To get sunday mass readings, run `./gen_readings.bat`

ICF uses Universalis, which I believe use NJB, but mass_readings.json uses another version, so update_mass_reading.py will update it to use NJB. Need to change mass_readings.json a bit, if there are any "or" readings (even though they already have 2 different readings, they didn't need the or), remove them and replace accordingly