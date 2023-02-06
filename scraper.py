import re
import lxml
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import tokenizer
from collections import defaultdict


frequencies = defaultdict(int)
most_words = ("", 0)


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page.
    # Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = []
    

    try: #catch any errors from urls
        if not(resp.status >= 200 and resp.status < 300 and resp.raw_response): #http status 200-299 is successful
            print(f"Error: {resp.error}")
            return [] #return an empty list  
        soup_content = BeautifulSoup(resp.raw_response.content.decode("utf-8", "ignore"), "lxml") #Should use lxml by default as long as lxml is installed in environment.
        if (is_high_quality_page(soup_content)): #check if page has lots of info or little and valid url
            global frequencies
            global most_words
            token_dict = tokenizer.compute_word_frequencies(tokenizer.tokenize(soup_content))
            frequencies = frequencies | token_dict   #combines new frequency dict with preexisting one
            totalWords = sum(token_dict.values())   #gets the sum of all the words in a single page
            if(totalWords > most_words[1]):      #checks if new page has more words than current max
                most_words = (soup_content, totalWords)   #replaces most_words with new page if it has more words
            for hyperlink in soup_content.find_all('a'): #get all the a tags inside html document
                hyperlink_href = hyperlink.get('href') #get out the link
                if (is_valid(hyperlink_href) and hyperlink_href != resp.url): #see if each link within the url is valid and not the same as link above
                    if "#" in hyperlink_href: #defragments the url
                        hyperlink_href = hyperlink_href[:hyperlink_href.find("#")]
                    links.append(hyperlink_href) #add to list to be added to fronteir later
        else: return []
        
        tokenizer.write_data("report.txt", frequencies, most_words)    #writes data of word frequencies and page with most words into a txt file

        return links
    except:
        return []


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return False
        if not re.match(r'(?:.+\.(?:i?cs|stat|informatics)\.uci\.edu$)', parsed.netloc):
            # theoretically, shouldn't be here if path is in allowed domains
            return False
        if not re.match(r'^/.*', parsed.path): # returns true if path is / followed by text
            return False
        if (is_trap(url)): #is_trap returns true if it is a trap
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
        print("TypeError for ", parsed)
        raise



def is_trap(url):
    known_traps = ["https://wics.ics.uci.edu/events", "/ppsx", "/pdf", "share="] #list of traps we found whilst running crawler
    for trap in known_traps:
        if (trap in url): #if the traps are included inside the url, then we can assume it is a trap
            return True
    return False

def is_high_quality_page(soup_content):
    bad_count = 100  # Minimum number of words for "low textual content" pages
    #get the html content and turns into a token list
    token_dict = tokenizer.compute_word_frequencies(tokenizer.tokenize(soup_content))   #
    token_sum = sum(list(token_dict.values()))
    if (token_sum <= bad_count): #see the quality count
        return False
    return True



if __name__ == "__main__":
    print("This is the website with the most words: ")
    double_sorted = sorted(sorted(frequencies.items(), key=(lambda x: x[0])), key=(lambda x: x[1]), reverse=True)
    for key, value in double_sorted[:50]:
        print(key, value, sep = ' - ')