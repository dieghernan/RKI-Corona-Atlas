from scrapy.commands.crawl import Command as ExistingCrawlCommand
from scrapy.exceptions import UsageError


class Command(ExistingCrawlCommand):

    def run(self, args, opts):
        if len(args) < 1:
            raise UsageError()
        elif len(args) > 1:
            raise UsageError("running 'scrapy crawl' with more than one spider is no longer supported")
        spname = args[0]

        crawl_defer = self.crawler_process.crawl(spname, **opts.spargs)

        if getattr(crawl_defer, 'result', None) is not None and issubclass(crawl_defer.result.type, Exception):
            self.exitcode = 1
        else:
            crawler = list(self.crawler_process.crawlers)[0]
            self.crawler_process.start()
            log_error = crawler.stats.get_value('log_count/ERROR')
            if (
                self.crawler_process.bootstrap_failed
                or hasattr(self.crawler_process, 'has_exception') and self.crawler_process.has_exception
                or log_error
            ):
                self.exitcode = 1
