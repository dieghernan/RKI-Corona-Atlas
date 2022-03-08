import locale

import scrapy
from scrap.spiders.rki_spider import RKISpider

try:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "German")


class ArchiveSpider(RKISpider):
    name = "archive"
    handle_httpstatus_list = [200, 404, 500]

    def start_requests(self):
        urls = [
            'file:///C:/Users/hernangomez/repos/RKI-Corona-Atlas/timelapse/archive/20200906204622.snapshot',
            'file:///C:/Users/hernangomez/repos/RKI-Corona-Atlas/timelapse/archive/20200925165513.snapshot',
            'file:///C:/Users/hernangomez/repos/RKI-Corona-Atlas/timelapse/archive/20201216183738.snapshot',
            'file:///C:/Users/hernangomez/repos/RKI-Corona-Atlas/timelapse/archive/20210319223005.snapshot',
            'file:///C:/Users/hernangomez/repos/RKI-Corona-Atlas/timelapse/archive/20210406142154.snapshot',
            'file:///C:/Users/hernangomez/repos/RKI-Corona-Atlas/timelapse/archive/20210514220848.snapshot',
            # TODO generate proper url list
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
