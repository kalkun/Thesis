
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

Add a symbolic link to the `protestDB` module:
```
ln -s `pwd`/protestDB venv/lib/python3.5/site-packages/protestDB
```
The above command assumes that the current directory is the project root folder.

### Migrate schema
Schema needs to be migrated using `alembic` whenever schematic changes occur, such as
a new table being added or columns being modified.

Migrations can be done from project root, using:
```
alembic revision --autogenerate
alembic upgrade head
```

### Configure
Set the path for the `*.db` SQLite file in the `config.py` file.

### Usage
This module will create the database file given by `config.py` if it does not exists
once the library is imported.

**Example usage:**
```python
from protestDB.cursor import ProtestCursor
# create a cursor:
pc = ProtestCursor()

# insert image file using `insertImage` method:
pc.insertImage(
   path_and_name = 'example_image.png',
   source        = 'google search',
   origin        = 'test',
   url           = 'example.com',
   tags          = ['protest', 'africa', 'example', 'test']
)
```

The above, will also make insertions into `Tags` table and link them to the image
through the `TaggedImages` table.

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

