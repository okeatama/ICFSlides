LITURGY_YEAR = "c" # just gonna hard code this since it changes not by year, but during advent

# try liturgy year, then a (since lagumisa uses a for special mass) then p for perayaan
tries = [LITURGY_YEAR, "a", "p"] 
FILENAMES = ["responsorial_psalm.png", "gospel_acclamation.png"] 
SLIDE_CONTENT_THRESHOLD = 375

NUM_TO_MONTH_ID = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

UNIVERSALIS_BASE_URL = "https://universalis.com/australia/"
LAGUMISA_BASE_URL = "https://www.lagumisa.web.id/lagumz.php?&f="
IMANKATOLIK_BASE_URL = "https://imankatolik.or.id" # e.g. https://imankatolik.or.id/kalender.php?b=11&t=2025

# slide layouts index
BIRTHDAY_LAYOUT = 0
FIRST_READING_LAYOUT = 1
SECOND_READING_LAYOUT = 2
GOSPEL_LAYOUT = 3
PSALM_LAYOUT = 4
GOSPEL_ACCLAMATION_LAYOUT = 5

# placeholders index
BIRTHDAY_PLACEHOLDER = 10

FIRST_READING_VERSES = 10
FIRST_READING_INDO = 11
FIRST_READING_EN = 12

SECOND_READING_VERSES = 10
SECOND_READING_INDO = 11
SECOND_READING_EN = 12

GOSPEL_VERSES = 10
GOSPEL_INDO = 11
GOSPEL_EN = 12

PSALM_VERSES = 10
PSALM_IMAGE = 11
PSALM_TEXT_INDO = 12
PSALM_TEXT_EN = 13

GOSPEL_ACCLAMATION_IMAGE = 10
GOSPEL_ACCLAMATION_TEXT_INDO = 11
GOSPEL_ACCLAMATION_TEXT_EN = 12