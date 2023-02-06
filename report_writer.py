import re
import os
from collections import defaultdict

def grab_pages(log_path):
    pages = set()
    pattern = re.compile(r'https?://[\\w./]+')
    with open("Worker.log", "r") as infile:
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


if __name__ == "__main__":
    cd = os.path.dirname(__file__)
    pages = grab_pages(os.path.join(cd, "Logs/Worker.log"))
    subdomains = count_subdomain(pages)
    with open("report.txt", "w") as outfile:
        outfile.write(f"1. The number of unique pages found during crawling is {len(pages)} pages")
        outfile.write(f"4. There were {len(subdomains)} subdomains under the ics.uci.edu domain.")
        for subdomain, count in subdomains.items():
            outfile.write(f"{subdomain}, {count}")
