import re
import os
from collections import defaultdict
import tokenizer
from bs4 import BeautifulSoup

def grab_pages(log_path):
    pages = set()
    pattern = re.compile(r'https?://[\\w./]+')
    with open(log_path, "r") as infile:
        for line in infile:
            match = pattern.search(line)
            if match:
                pages.add(match.group())
    return pages

def count_subdomain(pages):
    subdomains = defaultdict(int)
    for page in pages:
        match = re.match(r'https?://([\\w-]+).ics.uci.edu', page)
        if match:
            subdomain = match.group()
            subdomains[subdomain] += 1
    subdomains = dict(sorted(subdomains.items(), key=lambda x: (x[0], -x[1])))
    return subdomains

# def gather_words(pages):
#     frequencies = defaultdict(int)
#     most_words = ['', 0]
#     for page in pages:
#         soup_content = BeautifulSoup(page.raw_response.content.decode("utf-8", "ignore"), "lxml")
#         token_dict = tokenizer.compute_word_frequencies(tokenizer.tokenize(soup_content))
#         frequencies = frequencies | token_dict   #combines new frequency dict with preexisting one
#         totalWords = sum(token_dict.values())
#         if(totalWords > most_words[1]):      #checks if new page has more words than current max    
#             most_words = [soup_content, totalWords]
#     return frequencies


if __name__ == "__main__":
    cd = os.path.dirname(__file__)
    pages = grab_pages(os.path.join(cd, "Logs/Worker.log"))
    subdomains = count_subdomain(pages)
    # word_freq = gather_words(pages)
    # most_words = word_freq[1]
    with open("report.txt", "w") as outfile:
        outfile.write(f"1. The number of unique pages found during crawling is {len(pages)} pages")
        # outfile.write(f"2. The page {most_words[0]} has {most_words[1]} words, the most of any page.")
        # outfile.write("3.")
        # frequencies = word_freq[0]
        # double_sorted = sorted(sorted(frequencies.items(), key=(lambda x: x[0])), key=(lambda x: x[1]), reverse=True)
        # for key, value in double_sorted[:50]:
        #     outfile.write(f"{key} - {value}")
        outfile.write(f"4. There were {len(subdomains)} subdomains under the ics.uci.edu domain.")
        for subdomain, count in subdomains.items():
            outfile.write(f"{subdomain}, {count}")