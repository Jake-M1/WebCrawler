import json

class Stats:
    def __init__(self):
        #keep track of the four stats for the report
        self._unique_pages = set()
        self._longest_page = ['', 0]
        self._words = dict()
        self._ics_subdomains = dict()
        #if continuing a crawler (ex. if it crashes), load stats
        try:
            self.load_stats()
        except:
            pass
    
    def add_unique_page(self, url: str) -> None:
        #adds a url, will only add if unique beacuse it is a set
        self._unique_pages.add(url)

    def get_unique_pages(self) -> int:
        #return the length of the unique pages set
        return len(self._unique_pages)

    def change_longest_page(self, url: str, count: int) -> None:
        #check if the new page is longer, if so update the longest page
        if count > self._longest_page[1]:
            self._longest_page[1] = count
            self._longest_page[0] = url

    def get_longest_page(self) -> list:
        #return the longest page and number of words in list form
        return self._longest_page

    def add_common_word(self, word: str) -> int:
        #add the word to the dictionary and update the value
        if word in self._words:
            self._words[word] += 1
        else:
            self._words[word] = 1

    def get_common_words(self) -> list:
        words50 = []
        #get 50 top words sorted by frequency and then alphebetical
        for k,v in sorted(self._words.items(), key = lambda x: (-x[1], x[0])):
            if len(words50) < 50:
                words50.append(k)
            else:
                break
        return words50

    def add_ics_subdomain(self, subdomain_url: str, full_url: str) -> None:
        #add the url to the ics subdomain dictionary using sets
        if subdomain_url in self._ics_subdomains:
            self._ics_subdomains[subdomain_url].add(full_url)
        else:
            self._ics_subdomains[subdomain_url] = set(full_url)

    def get_ics_subdomains(self) -> list:
        subdomains = []
        #get the ics subdomains and number of unique pages in each
        for k,v in sorted(self._ics_subdomains.items(), key = lambda x: x[0]):
            subdomains.append(f'{k}, {len(v)}')
        return subdomains

    def display_stats(self) -> str:
        #generate a string report using the stored stats
        report = 'REPORT:\n\n\n'
        report += f'Unique pages: {self.get_unique_pages()}\n\n'
        report += f'Longest page: {self.get_longest_page()[0]}, {self.get_longest_page()[1]}\n\n'
        report += '50 most common words (ignoring English stop words):\n'
        word_rank = 1
        for word in self.get_common_words():
            report += f'{word_rank}. {word}\n'
            word_rank += 1
        report += '\n'
        report += f'{len(self._ics_subdomains.keys())} Subdomains in ics.uci.edu:\n'
        for subdomain in self.get_ics_subdomains():
            report += f'{subdomain}\n'
        report += '\n'
        report += '\nEND OF REPORT'
        return report

    def write_report(self, path: str) -> None:
        file = None
        #write the report to the designated file
        try:
            file = open(path, 'w')
            file.write(self.display_stats())
        except:
            raise
        finally:
            if file != None:
                file.close()

    def save_stats(self):
        subdomain_lists = dict()
        #transform some data from set to list so json will work
        for k,v in self._ics_subdomains.items():
            subdomain_lists[k] = list(v)
        #use json to dump the stats to a local text file for a backup
        with open('stats_dump.txt', 'w') as file:
            json.dump([list(self._unique_pages), self._longest_page, self._words, subdomain_lists], file)

    def load_stats(self):
        #use json to load the stats to the latest backup text file
        with open('stats_dump.txt', 'r') as file:
            stats = json.load(file)
        self._unique_pages = set(stats[0])
        self._longest_page = stats[1]
        self._words = stats[2]
        #turn the data from list back into sets
        for k,v in stats[3].items():
            self._ics_subdomains[k] = set(v)

