from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
import stats


class Worker(Thread):
    def __init__(self, worker_id, config, frontier, stats):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.stats = stats
        self.backup_counter = 0
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        #i = 0
        #while i < 20:
            #i += 1
        while True:
            #backup the stats and simhashes to local files after every ten runs
            if self.backup_counter >= 10:
                self.stats.save_stats()
                self.frontier.save_simhash_index()
                self.backup_counter = 0
            else:
                self.backup_counter += 1

            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp, self.stats, self.frontier)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
