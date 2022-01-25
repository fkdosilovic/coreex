# CoreEx: Content Extraction from Online News Articles

This the (unofficial) implementation of [*CoreEx: Content Extraction from Online News Articles*](http://ilpubs.stanford.edu:8090/832/) by Jyotika Prasad & Andreas Paepcke.

**As opposed to the parent repository, this fork aims to implement the
algorithm as it is described in the paper.**

Code is packaged to enable easier experimentation.

## Installation

1. Clone this repository
2. Inside the repository run `pip install .`

## Example

```python
from lxml import etree
from coreex import summary # or import coreex

content = summary(str(path)) # or coreex.summary
content_str = etree.tostring(content, pretty_print=True, encoding=str)
```

## ToDo

- [ ] Change interface so that user selects the HTML parser, i.e. `summary` will
accept tree instead of string.
- [ ] Refactor the code to use beautifulsoup's DOM tree
- [ ] Refactor the code to use Pythonic naming conventions
- [ ] Enable hyperparameter selection.
- [ ] Make preprocessing more explicit!