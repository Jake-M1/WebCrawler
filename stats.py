from collections import defaultdict

class Stats:
    def __init__(self):
        self._unique_pages = set()
        self._longest_page = 0
        self._words = defaultdict(int)
        self._ics_subdomains = defaultdict(int)
    
    def add_unique_page(self, url: str) -> None:
        self._unique_pages.add(url)

    def get_unique_pages(self) -> int:
        return len(self._unique_pages)

    def change_longest_page(self, count: int) -> None:
        if count > self._longest_page:
            self._longest_page = count

    def get_longest_page(self) -> int:
        return self._longest_page

    def add_common_word(self, word: str) -> int:
        self._words[word] += 1

    def get_common_words(self) -> list(str):
        words50 = []
        for k,v in sorted(self._words.items(), key = lambda x: (-x[1], x[0])):
            if len(words50) < 50:
                words50.append(k)
            else:
                break
        return words50

    def add_ics_subdomain(self, url: str, pages: int) -> None:
        self._ics_subdomains[url] = pages

    def get_ics_subdomains(self) -> list(str):
        subdomains = []
        for k,v in sorted(self._ics_subdomains.items(), key = lambda x: x[0]):
            subdomains.append(f'{k}, {v}')
        return subdomains
