import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    res = {}
    # Each page can be randomly chossen with the porbability of (1-d)/N
    random_prob = (1-damping_factor)/(len(corpus))
    for key in corpus.keys():
        res[key] = random_prob

    # Probability of links that can be clicked from the current page
    if corpus[page] is not None:
        click_prob = damping_factor/(len(corpus[page]))
        for elem in corpus[page]:
            res[elem] += click_prob

    return res


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Page for the inital sample
    page = random.choice(list(corpus.keys()))
    res = None
    for i in range(n):
        res = transition_model(corpus, page, damping_factor)
        # Pick a random value from 0 to 1, and then go to the page that
        # coresponds to that value.
        done = False
        while done == False:
            ran = random.random()
            cur = 0
            for key, val in res.items():
                if ran >= cur and ran < cur+val:
                    page = key
                    done = True
                    break
                cur += val
    return res


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    res = {}
    length = len(corpus)
    # Each page is equally likely to be picked
    prob = 1/length
    for key in corpus.keys():
        res[key] = prob
    # Keep running until values do not change by about 0.001
    done = False
    while done == False:
        temp = {}
        for key in corpus.keys():
            total = 0
            for val in corpus[key]:
                if corpus[val] != None:
                    total += res[val]/(len(corpus[val]))
                else:
                    total += 0/length

            temp[key] = (1-damping_factor)/length + damping_factor*total

        done = True
        for key in res.keys():
            if abs(res[key] - temp[key]) > 0.001:
                done = False
        res = temp

    return res


if __name__ == "__main__":
    main()
