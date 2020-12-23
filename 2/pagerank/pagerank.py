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
    if corpus[page] is not None and len(corpus[page]) != 0:
        click_prob = damping_factor/(len(corpus[page]))
        for elem in corpus[page]:
            res[elem] += click_prob
    # if there are no outgoing links, each page should be equally likely
    else:
        for key in res.keys():
            res[key] = 1/len(corpus)

    return res


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Inital the result dictionary
    res = dict()
    for key in corpus.keys():
        res[key] = 0

    # Generate a random value for the first sameple
    page = random.choice(list(corpus.keys()))
    res[page] = 1

    # Start to sample based on the previous page
    for i in range(1, n):
        model = transition_model(corpus, page, damping_factor)
        page = random.choices(list(model.keys()), weights=list(model.values()))[0]
        res[page] += 1

    # Divide all of the results by n to get percentages
    for key in res.keys():
        res[key] = res[key]/n

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

    # At first assume that each page is equally likely to be picked
    prob = 1/length
    for key in corpus.keys():
        res[key] = prob

    # Keep running until values do not change by about 0.001
    done = False
    while done == False:
        done = True
        temp = {}
        for key in res.keys():
            temp[key] = (1-damping_factor)/length
            total = 0
            for k in res.keys():
                if key in corpus[k]:
                    total += damping_factor*res[k]/(len(corpus[k]))
            temp[key] += total

            if abs(res[key] - temp[key]) > 0.0005:
                done = False

        for key in res.keys():
            res[key] = temp[key]

    return res

if __name__ == "__main__":
    main()


