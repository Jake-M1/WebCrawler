import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import stats

def scraper(url, resp, stats, frontier):
    links = extract_next_links(url, resp, stats, frontier)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp, stats, frontier):
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
    #check response status first, if not in good range, do not crawl or process
    if (resp.status < 200 or resp.status > 299):
        return links

    #check for dead url that return a 200 status but no data
    if resp.raw_response == None:
        return links
    
    #defragment the url and add to set of unique pages
    home_url = resp.url.split('#', 1)[0]
    stats.add_unique_page(home_url)

    #parse url and add it to ics subdomain stats if it is in the ics domain
    parsed = urlparse(home_url)
    if re.search(r'\.ics\.uci\.edu', parsed.netloc) != None:
        subdomain_url = f'{parsed.scheme}://{parsed.netloc}'
        stats.add_ics_subdomain(subdomain_url, home_url)

    #use beautiful soup to parse the HTML
    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    text = soup.get_text()

    #tokenize text and do not crawl if the page is low info
    tokens = tokenize(text)
    if detect_low_info(tokens) == True:
        return links

    #calculate simhash value for page content and check similarity
    simhash = get_simhash(tokens)
    if detect_duplicate(simhash, frontier, 0.95) == True:
        return links
    else:
        frontier.add_simhash_index(simhash)

    #if page is good to crawl, get the links and process the text
    for link in soup.find_all('a'):
        link = link.get('href')
        if (is_valid(link)):
            link_defragment = link.split('#', 1)[0]
            if re.search(r'evoke.ics.uci.edu', link_defragment) == None or re.search(r'replytocom', link_defragment) == None:
                if len(link_defragment) < 150:
                    links.append(link_defragment)

    process_text(tokens, home_url, stats)

    return links


def is_valid(url) -> bool:
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        #see if url matches the wanted domains using regular expressions
        if re.search(r'(\.ics\.uci\.edu)|(\.cs\.uci\.edu)|(\.informatics\.uci\.edu)|(\.stat\.uci\.edu)|(today\.uci\.edu)', parsed.netloc) == None:
            return False
        if re.search(r'today\.uci\.edu', parsed.netloc) != None:
            if re.search(r'/department/information_computer_sciences', parsed.path) == None:
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
        print ("TypeError for ", url)
        raise


def tokenize(text: str) -> list:
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


def process_text(tokens: list, url: str, stats) -> None:
    #list of stop words to not count in common words
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

    for token in tokens:
        #only count a token as a common word if it is not a stop word, is more than one character, and has no numbers
        if token not in stop_words and len(token) > 1 and re.search(r'\d', token) == None:
            stats.add_common_word(token)
    #all tokens go into the longest page stat
    stats.change_longest_page(url, len(tokens))

def detect_duplicate(simhash: str, frontier, threshold: float) -> bool:
    s1 = int(simhash, 2)
    #compare the given simhash to all unique simhashes found before
    for shash in frontier.get_simhash_index():
        #calculate similar bits in the fingerprints
        s2 = int(shash, 2)
        i = s1 ^ s2
        diff = 0.0
        while i:
            i = i & (i-1)
            diff += 1.0
        #using 32 bit fingerprints
        similar = 32.0 - diff
        #if the number of similar bits divided by total bits is greater than the given threshold, return true
        if similar/32.0 >= threshold:
            return True
    return False

def detect_low_info(tokens: list) -> bool:
    words = 0
    #a page is low info if it has less than 10 words (word-like phrases)
    for token in tokens:
        if len(token) > 1 and re.search(r'\d', token) == None:
            words += 1
        if words >= 10:
            return False
    return True

def compute_word_frequencies(token_list: list) -> dict:
    token_count = dict()
    for token in token_list:
        #if the token is already in the dict, add its count +1
        if token in token_count:
            token_count[token] += 1
        #if not, set the count to 1
        else:
            token_count[token] = 1
    return token_count

def get_simhash(tokens: list) -> str:
    #defining weights as the frequency of the tokens
    weights = compute_word_frequencies(tokens)
    binary = dict()
    #get the 32 bit binary hash for each token
    for k in weights.keys():
        binary[k] = hash32b(k)
    bit = 31
    fingerprint = ''
    #go through each bit of each hashed token and calculate the fingerprint based on weights
    while bit >= 0:
        vec = 0
        for k,v in binary.items():
            if v[bit] == '0':
                vec -= weights[k]
            else:
                vec += weights[k]
        if vec > 0:
            fingerprint = '1' + fingerprint
        else:
            fingerprint = '0' + fingerprint
        bit -= 1
    return fingerprint

def hash32b(token: str) -> str:
    #use the default python hash function
    hashint = hash(token)
    b = 2**32
    #mod it so can be represented by 32 bits
    hashbin = f'{hashint % b:b}'
    #add extra zeros to the front if neccessary
    while len(hashbin) < 32:
        hashbin = '0' + hashbin
    return hashbin

