
## ProtestDB

### Data infrastructure
This resource defines setup of interfacing with the dataset in SQLite
using the python library sqlalchemy.

See the [documentation for the SQLite schema](https://drive.google.com/file/d/19qylIx8-6J9nAEF1DTEQOOJ9QJUFX_mo/view?usp=sharing)

### SETUP

Setup a virtual environemnt:
```
pyvenv venv
```
Then, activate environment and install requirements:
```
source venv/bin/activate
pip install -r requirements.txt
```


### Configure
Set the path for the `*.db` SQLite file in the `config.py` file.

### Usage
This module will create the database file given by `config.py` if it does not exists
once the library is imported.

**Example usage:**
```python
import protestDB
# create a cursor:
dbCursor = protestDB.engine.ProtestCursor()

# insert image file using `insertImage` method:
dbCursor.insertImage(
   path_and_name = 'example_image.png',
   source        = 'google search',
   imgtype       = 'local',
)
```

See the class `ProtestCursor` in the file protestDB.engine for
documentation on the possible parameters and their meaning.



## Serp Scraper

This code defines a commandline interface for scraping images.

Get usage information:
```
python serp_driver.py --help
```
Otherwise the general idea is to provide a path to a directory where the images
scraped will be saved, the key word to be scraped (currently supports only one)
and the search engines (currently only supports google). Look in the help for 
additional arguments
```
python serp_driver.py  images --sr google --key_words "jenifer anistion" "pamela anderson" --limitres 15
```

