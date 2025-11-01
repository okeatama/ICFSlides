from string import digits
import json

psalms = dict()

with open("resources/raw.txt", "r", encoding="utf-8") as file:
    # raw.txt source from https://bibletold.com/psalms
    for line in file:
        if line == "":
            # skip empty line
            continue

        if line[0] not in digits:
            # not a verse, skip
            continue

        # line starts with a digit, which is the text
        # format is {chapter}:{verse} {text}
        chapterverse, text = line.split(" ", 1)

        # post-adjustment. strip() to remove hanging \n, and replaces to change unicode characters
        text = text.strip().replace(u"\u2018", "'").replace(u"\u2019", "'").replace(u"\u2013", "-").replace(u"\u201c", '"').replace(u"\u201d", '"')

        chapter, verse = chapterverse.split(":")

        if chapter not in psalms:
            # new chapter, dictionary not in current dict
            new_chap = dict()
            new_chap[verse] = text

            psalms[chapter] = new_chap
        else:
            # chapter already in the psalm, so just add into it
            psalms[chapter][verse] = text

with open("JSON/psalm.json", "w") as file:
    json.dump(psalms, file, indent=4)