# skweak: Weak supervision for NLP

What is `skweak`? `skweak` (pronounced `/skwiːk/`) is a Python-based software toolkit to apply weak supervision to NLP tasks. Instead of annotating texts by hand, you can use `skweak` to automatically label text documents by defining a set of _labelling functions_ and then _aggregating_ their results to obtain a labelled version of your corpus. 

`skweak` can be applied to both sequence labelling and text classification, and comes with a complete API that makes it possible to create, apply and aggregate labelling functions with just a few lines of code. Give it a try!

For more details on `skweak`, see our paper (...).

## Requirements

The following Python packages must be installed:
- `spacy` >= 2.2 (both v2 or v3 should work)
- `hmmlearn` >= 0.2.4
- `pandas` >= 0.23
- `numpy` >= 1.18

`skweak` has been developed with Python 3.x (we haven't tested it for Python 2.x, but it might be possible to get it to work).

TODO: make `skweak` into a full-blown package that can be installed through `pip install`. 

## Basic Overview

<br>
<p align="center">
   <img alt="Overview of skweak" src="https://raw.githubusercontent.com/NorskRegnesentral/skweak/main/data/skweak_procedure.png"/>
</p><br>

The use of weak supervision with `skweak` goes through the following steps:
- *Step 0*: First, you need raw (unlabelled) data from your text domain. `skweak` is build on top of [SpaCy](http://www.spacy.io), and operates with Spacy `Doc` objects, so you first need to convert your documents to `Doc` objects with `spacy`.
- *Step 1*: Then, we need to define a range of labelling functions that will take those documents and annotate spans with labels. Those labelling functions can take a variety of forms, such as heuristics, gazetteers, machine learning models or even results from crowd-workers. See the ![documentation](https://github.com/NorskRegnesentral/skweak/wiki) for more details. 
- *Step 2*: Once the labelling functions have been applied to your corpus, you need to _aggregate_ their results in order to obtain a single annotation layer (instead of the multiple, possibly conflicting annotations from the labelling functions). This is done in `skweak` using a generative model that automatically estimates the relative accuracy and possible confuctions of each labelling function. 
- *Step 3*: Finally, based on those aggregated labels, we can train our final model. Step 2 gives us a labelled corpus that (probabilistically) aggregates the outputs of all labelling functions, and you can use this labelled data to estimate any kind of machine learning model. You are free to use whichever model/framework you prefer. 

## Quickstart

Here is a minimal example with three labelling functions (LFs) applied on a single document:

```python
import spacy, re
from skweak import heuristics, gazetteers, aggregation, utils

# LF 1: heuristic to detect occurrences of MONEY entities
def money_detector(doc):
   for i, tok in enumerate(doc[1:]):
      if tok.text[0].isdigit() and tok.nbor(-1).is_currency:
          yield (i-1,i+1, "MONEY")
lf1 = heuristics.FunctionAnnotator("money", money_detector)

# LF 2: detection of years with a regex
lf2= heuristics.TokenConstraintAnnotator ("years", lambda tok: re.match("(19|20)\d{2}$", tok.text), "DATE")

# LF 3: a gazetteer with a few names
NAMES = [("Barack", "Obama"), ("Donald", "Trump"), ("Joe", "Biden")]
trie = gazetteers.Trie(NAMES)
lf3 = gazetteers.GazetteerAnnotator("presidents", trie, "PERSON")

# We create a corpus (here with a single text)
nlp = spacy.load("en_core_web_md")
doc = nlp("Donald Trump paid $750 in federal income taxes in 2016")

# apply the labelling functions
doc = lf3(lf2(lf1(doc)))

# and aggregate them
hmm = aggregation.HMM("hmm", ["PERSON", "DATE", "MONEY"])
hmm.fit_and_aggregate([doc])

# we can then visualise the final result
hmm.utils.display_entities(doc, "hmm")
```

Obviously, to get the most out of `skweak`, you will need more labelling functions, and a larger corpus including as many documents as possible from your domain. 
