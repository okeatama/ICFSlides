import scrapy
from bible_chapters import catholic_bible_chapters

BASE_URL = "https://www.catholic.org/bible/book.php?id="

class ReadingsSpider(scrapy.Spider):
    name = "readings"

    async def start(self):
        urls = []
        id = getattr(self, "id", None)
        if id is None or not id.isdigit():
            raise scrapy.exceptions.CloseSpider("id not given or is not digit")
        id = int(id)
        
        _, chapter_amount = catholic_bible_chapters[id]

        for i in range(1, chapter_amount + 1):
            urls.append(f"{BASE_URL}{id + 1}&bible_chapter={i}")

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        verses = response.xpath('//div[@id="bibleBook"]/p//text()').getall()
        verse_num = verses[0]
        verse_text = ""
        res = dict()

        for verse in verses[1:]:
            if verse.isdigit():
                if verse_num == 0:
                    verse_num = verse
                    continue
                else:
                    res[verse_num] = verse_text
                    verse_num = verse
                    verse_text = ""

            else:
                verse_text = verse_text + verse
        res[verse_num] = verse_text

        yield res