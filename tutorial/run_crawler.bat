@REM call scrapy crawl readings -O 45.json -a id=45

for /L %%n in (1,1,72) do scrapy crawl readings -O %%n.json -a id=%%n --logfile %%n.txt