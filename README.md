# Project Doom

Project Doom is a group of 4 of libraries used for in depth analysis of rap lyrics. Doom specifically focuses on rap verses; where other libraries analyze all lyrics of a song, Doom utilizes complex but rhobust filtering to extract verses and verses specific to indibidual artists. Doom is written to be powerful enough for advanced programmers to use/tweak for their own research and simple enough for new comers/non-technical rap enthusiasts to utilize. By using container functions and detailing the start to finish, full scrape to vizualization process in full_proc.ipynb, I hope people from all expertise backgrounds can enjoy and learn something new. Please use/tweak full_proc.ipynb for a simple and high level guide to using the libraries, this readme goes into depth regarding each function and object within each library.

Doom is broken up into 4 libraries, each designed with a focused purpose addressing the full scrape to vizualization journey. Here are the libraries and their primary functionality/capabilties:

###rap_scrpr
This library is used to scrape rap lyrics website http://ohhla.com. For the most part, lyrics are organized in generally the same format with consistent labeling making the cleaning process simpler.

###rap_db
While not inherently necessary, this library is comprised of a group of functions to interact with a PostgreSQL database full of rap lyrics. It manages the entire data storage process, table creation, populating the database, and quereying it.

###rap_clean
This is the most complex of the four libraries as it tackles the most challenging part of data retrieval. Per its name, it cleans and prunes lyrics stored in raw text data and extracts songs segments (intro, verse, chorus, outro, misc.). This project is dedicated to verses so there are additional filtering and objects/methods (word syllable extraction) focused on verses.

###rap_viz
This library uses specialized artist, song, and verse objects created in rap_clean to vizualize lingustic meta data, verse syllable breakdowns, and verse sorting/rankings. The functions in rap_viz can also be used as a template for creating complex, more specific, or more dynamic vizualizations based on user preference.

###rap_mach
This library is undergoing development. You may be able to guess by its name what it might do.

##Installing and Library Dependencies

###Installing Doom
```
pip install git+git://github.com/m4n0b0dy/doom
NEWCOMERS - This does not install all the other libraries necessary to run Doom
```

###Library Dependencies
I'm not shy about using other libraries, and given the different goals of each library, they use a ton of external functions. Here are the dependenceis broken up by library; once a library has been listed, it isn't re-listed when imported again in a different Doom library. For your own sanity, I would HIGHLY recommend using Anaconda and installing all the unincluded ones individually.

###rap_scrpr
```
import json
import re
from bs4 import BeautifulSoup
import urllib
import time
```
###rap_db
```
import psycopg2 as pg2
import psycopg2.extras
import pickle as pic
from os import listdir
from os import path
from os.path import isfile, join
```
###rap_clean
```
from nltk.corpus import stopwords
from nltk.stem import *
from difflib import SequenceMatcher
from difflib import get_close_matches
from nltk.corpus import cmudict
import pyphen
```
###rap_viz
```
from statistics import mean, median
import plotly.offline as offline
import plotly.figure_factory as ff
import plotly.graph_objs as go
from collections import Counter
from random import shuffle
from IPython.core.display import display, HTML
from copy import deepcopy
```

#temp stufff

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```
