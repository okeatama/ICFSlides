import json
from tutorial.bible_chapters import books

bible = []

for i in range(73):
    with open(f"bible/{i}.json", "r") as file:
        book = json.load(file)
    
    book_name = books[i]
    updated_book = []
    
    for b in book:
        updated_book.append(list(b.values()))
    
    bible.append(updated_book)

with open("bible/bible.json", "w") as file:
    json.dump(bible, file, indent=4)
    