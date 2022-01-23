import re
import unicodedata

from lxml import html, etree

"""This module can be used in order to extract the main content from blog
posts/news using the algorithm described in the paper "CoreEx:
Content Extraction from Online News Articles" by Jyotika Prasad & Andreas
Paepcke (available here: http://ilpubs.stanford.edu:8090/832/).

The only "public" function is summary.
"""

# __all__ = ["summary"]

threshold = 0.9
weight_ratio = 0.95
weight_text = 0.05


def preprocess(element):
    """Drop all the tree where the root is one of the following:
    * <img>
    * <form>
    * <iframe>
    * <script>
    * <style>
    * <!-- comments -->

    This operate directly on element (i.e. no return value).
    """
    forbidden = [
        "img",
        "span",
        "video",
        "button",
        "select",
        "iframe",
        "script",
        "noscript",
        "style",
        etree.Comment,
    ]
    etree.strip_elements(element, with_tail=False, *forbidden)


def normalize(txt):
    """Remove all the unicode "marks", e.g.:
    >>> normalize('un éléphant ça trompe énormément!')
    'un elephant ca trompe enormement!'
    """
    nfkd = unicodedata.normalize("NFKD", txt)
    return "".join(x for x in nfkd if unicodedata.category(x)[0] != "M")


def count_words(txt):
    """Count the number of words in txt."""
    txt = normalize(txt)
    return len(re.findall(r"\w+", txt))


def create_subsets(elt):
    """Set the textCnt, linkCnt, setTextCnt, and setLinkCnt variables
    to the right value to elt and to all its subtree recursively.
    """
    if elt.tag == "a":
        elt.textCnt = 1
        elt.linkCnt = 1

    else:
        elt.textCnt = count_words(elt.text or "")
        elt.linkCnt = 0
        elt.setTextCnt = elt.textCnt
        elt.setLinkCnt = 0

        elt.S = set()

        for child in elt:
            create_subsets(child)
            elt.textCnt += child.textCnt
            elt.linkCnt += child.linkCnt

            tailTextCnt = count_words(child.tail or "")
            elt.textCnt += tailTextCnt
            elt.setTextCnt += tailTextCnt

            if child.textCnt > 0:
                childRatio = (child.textCnt - child.linkCnt) / child.textCnt

                if childRatio > threshold:
                    elt.S.add(child)
                    elt.setTextCnt += child.textCnt
                    elt.setLinkCnt += child.linkCnt


def score_node(element, page_text):
    """Score the node using the formula:
    score = weight_ratio * (setTextCnt - setLinkCnt) / setTextCnt
          + weight_text * setTextCnt / page_text
    """
    try:
        if "S" in element.__dict__:
            element.score = (
                weight_ratio
                * (element.setTextCnt - element.setLinkCnt)
                / element.setTextCnt
                + weight_text * element.setTextCnt / page_text
            )
    except ZeroDivisionError:
        pass  # no text? no score, fair enough?


def set_scores(elements, page_text=None):
    """Set the score of all elements in the subtree using the score_node
    function.

    page_text is equal to the number of words in the whole tree,
    you probably don't want to use it.
    """
    page_text = page_text or elements.textCnt

    for child in elements:
        set_scores(child, page_text)

    score_node(elements, page_text)


def summary(filename: str, parser=None, base_url=None):
    """Take the same arguments as html.parse.

    Return an lxml element which (hopefully) contains all the content.
    """

    document = html.parse(filename, parser, base_url)
    root = document.getroot()
    body = root.body

    # Hackish and ugly, but needed to add data to each node ...
    # https://mailman-mail5.webfaction.com/pipermail/lxml/2010-April/005368.html
    alive = set(body.iterdescendants()) | {body}

    preprocess(body)
    create_subsets(body)
    set_scores(body)

    best = max(alive, key=lambda x: x.score if "score" in x.__dict__ else 0)

    for e in best:
        try:
            if e not in best.S:
                e.drop_tree()
        except Exception:
            e.drop_tree()

    return best
