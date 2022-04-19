import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import stats

def scraper(url, resp, stats):
    links = extract_next_links(url, resp, stats)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp, stats):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

    links = []
    if (resp.status != 200):
        return links

    

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    for link in soup.find_all('a'):
        if (is_valid(link)):
            link_defragment = link.split('#', 1)[0]
            links.append(link_defragment)
            #links.append(link)

    text = soup.get_text()
    process_text(text, stats)

    return links


def is_valid(url) -> bool:
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if re.search(parsed.netloc, r'ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu|today.uci.edu') == None:
            return False
        if re.search(parsed.netloc, r'today.uci.edu') != None:
            if re.search(parsed.path, r'/department/information_computer_sciences') == None:
                return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


def tokenize(text: str) -> list(str):
    tokens = []
    #use regular expressions to slip line by any non English alphanumeric char (special, whitespace, etc)
    words = re.split(r'[^a-zA-Z0-9]+', text.lower().strip(), flags = re.ASCII)
    #this if else statement is instead of checking each word
    #gets rid of empty line token
    if len(words) == 1 and words[0] == '':
        pass
    #fixes if a line starts and ends with a special char
    elif words[0] == '' and words[len(words) - 1] == '':
        tokens += words[1:len(words) - 1]
    #fixes if a line starts with a special char
    elif words[0] == '':
        tokens += words[1:]
    #fixes if a line ends with a special char
    elif words[len(words) - 1] == '':
        tokens += words[:len(words) - 1]
    #normal add tokens on that line to total token list
    else:
        tokens += words
    return tokens


def process_text(text: str, stats) -> None:
    stop_words = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and']
    stop_words += ['any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being']
    stop_words += ['below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did']
    stop_words += ["didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few']
    stop_words += ['for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having']
    stop_words += ['he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him']
    stop_words += ['himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if']
    stop_words += ['in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me']
    stop_words += ['more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off']
    stop_words += ['on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out']
    stop_words += ['over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't"]
    stop_words += ['so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them']
    stop_words += ['themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've"]
    stop_words += ['this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was']
    stop_words += ["wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's"]
    stop_words += ['when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why']
    stop_words += ["why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll", "you're", "you've"]
    stop_words += ['your', 'yours', 'yourself', 'yourselves']

    tokens = tokenize(text)
    for token in tokens:
        if token not in stop_words:
            stats.add_common_word(token)
    
    stats.change_longest_page(len(tokens))
