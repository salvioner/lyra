LYRA by Arighi Andrea and Riccardo Tosin

SETUP INSTRUCTIONS after cloning this repository in a local folder:

1) Edit file config.py to fit your computer's configuration.

2) Download the dataset
* Either clone the repository https://github.com/salvioner/lyra-dataset.git inside the "dataset" folder
* Or regenerate the dataset from scratch (last tested: February 2016)
    - run dataset/fetchAlbums.py
    - run dataset/fetchSongs.py
    NOTE: this will take quite a long time, since the script will attempt to download more than 10.000 song texts from lyricswikia. A working Internet connection is required for both scripts to work.

3) Download additional packages (I suggest the use of Anaconda distribution of Python, which includes almost all of the required packages: https://www.anaconda.com/what-is-anaconda/)
* Package requirements for alg.py:
vaderSentiment
numpy
glob
json

* Package requirements for dboperations.py:
numpy
matplotlib.pyplot
sklearn.cluster
glob

* Package requirements for dataset scripts:
BeautifulSoup4 (AKA: bs4)
urllib2
codecs

4) For help, run:
      python start.py -h
from the root folder (where this file is saved). 
