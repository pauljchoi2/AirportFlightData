from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.spiders import yeg_spider, ylw_spider, yqb_spider, ytz_spider, yul_scraper, yvr_spider, yyc_spider, yyj_spider, yyz_spider

if __name__ == '__main__':
    crawler  = CrawlerProcess(get_project_settings())
    crawler.crawl(yeg_spider.YEGSpider)
    crawler.crawl(ylw_spider.YLWSpider)
    crawler.crawl(yqb_spider.YQBSpider)
    crawler.crawl(ytz_spider.YTZSpider)
    crawler.crawl(yul_scraper.YULSpider)
    crawler.crawl(yvr_spider.YVRSpider)
    crawler.crawl(yyc_spider.YYCSpider)
    crawler.crawl(yyj_spider.YYJSpider)
    crawler.crawl(yyz_spider.YYZSpider)
    crawler.start()


    