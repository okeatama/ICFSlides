from tutorial.bible_chapters import books, catholic_bible_chapters
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

with open("JSON/mass_readings.json", "r") as file:
    readings = json.load(file)

with open("bible/bible.json", "r") as file:
    bible = json.load(file)

accepted_types = ["READING", "GOSPEL"]

# best use debugger to play around with the json, very confusing otherwise
for i, reading in enumerate(readings):
    sections = reading["sections"]
    if sections == []:
        continue

    for j, section in enumerate(sections):
        if section["type"] not in accepted_types:
            continue
        
        for k, r in enumerate(section["readings"]):

            verses = r["verses"][0]
            # in the form of {BOOK_NAME} {CHAPTER_NUM}:{VERSE_START}-{VERSE_END}

            book_name = verses["book"]
            book_num = books.index(book_name)

            # remove book name, so it should now only be {CHAPTER_NUM}:{VERSE_START}-{VERSE_END}
            verse_split = verses["text"][len(book_name) + 1:].strip().replace(";", ",")

            whole_text = ""
            # possibility of there being 2
            for comma_split in verse_split.split(","):
                # comma_split is in the form {CHAPTER_NUM}:{VERSE_START}-{VERSE_END}
                # or just {VERSE_START}-{VERSE_END}, if so then use same chapter

                if ":" not in comma_split:
                    # some books only have 1 chapter, so chapter is never mentioned
                    chapter = 0
                
                
                chapter_verse = comma_split.split(":")

                if len(chapter_verse) != 1:
                    # chapter given
                    
                    chapter = int(chapter_verse[0]) - 1

                    if "-" not in chapter_verse[1]:
                        # only one verse
                        # chapter_verse = [{CHAPTER_NUM}, {VERSE}]
                        verse = chapter_verse[1].strip()

                        if not verse.isdigit():
                            # some use a,b,c to denote which part of the verse, but since there is no logical
                            # way to cut it off in program, just give the whole verse
                            print(f"WARNING: there is alphabet in verse: {verse}")
                            verse = verse[:-1]

                        verse = int(verse)

                        text = bible[book_num][chapter][verse]
                        whole_text += text.strip()
                    else:
                        # chapter_verse = [{CHAPTER_NUM}, {VERSE_START}-{VERSE_END}]
                        verse_start, verse_end = chapter_verse[1].split("-")
                        verse_start = verse_start.strip()
                        verse_end = verse_end.strip()

                        # some use a,b,c to denote which part of the verse, but since there is no logical
                        # way to cut it off in program, just give the whole verse
                        if not verse_start.isdigit():
                            print(f"WARNING: there is alphabet in verse_start, double check: {verse_start}")
                            verse_start = verse_start[:-1]
                        if not verse_end.isdigit():
                            print(f"WARNING: there is alphabet in verse_end, double check: {verse_end}")
                            verse_end = verse_end[:-1]

                        verse_start = int(verse_start) - 1
                        verse_end = int(verse_end) - 1

                        text = "".join(bible[book_num][chapter][verse_start:verse_end])
                        whole_text += text.strip()
                else:
                    # no chapter given
                    # use previous chapter
                    if "-" not in comma_split:
                        # only 1 verse, so no start-end. comma_split = {VERSE}
                        verse = comma_split.strip()

                        if not verse.isdigit():
                            # some use a,b,c to denote which part of the verse, but since there is no logical
                            # way to cut it off in program, just give the whole verse
                            print(f"WARNING: there is alphabet in verse: {verse}")
                            verse = verse[:-1]
                        
                        verse = int(verse)

                        text = bible[book_num][chapter][verse]
                        whole_text += text.strip()
                    else:
                        # comma_split = {VERSE_START}-{VERSE_END}
                        verse_start, verse_end = comma_split.split("-")
                        verse_start = verse_start.strip()
                        verse_end = verse_end.strip()

                        # some use a,b,c to denote which part of the verse, but since there is no logical
                        # way to cut it off in program, just give the whole verse
                        if not verse_start.isdigit():
                            print(f"WARNING: there is alphabet in verse_start: {verse_start}")
                            verse_start = verse_start[:-1]
                        if not verse_end.isdigit():
                            print(f"WARNING: there is alphabet in verse_end: {verse_end}")
                            verse_end = verse_end[:-1]
                        
                        verse_start = int(verse_start) - 1
                        verse_end = int(verse_end) - 1

                        text = "".join(bible[book_num][chapter][verse_start:verse_end])
                        whole_text += text.strip()

            readings[i]["sections"][j]["readings"][k]["text"] = whole_text.strip()
    
# save into json file
with open("JSON/updated_mass_readings.json", "w") as file:
    json.dump(readings, file, indent=4)