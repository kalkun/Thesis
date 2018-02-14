
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

Configurations are set in `alembic.ini`. Especially the following two fields are relevant to set:
```
# DB name: 
db_name = protest_images.db

# image location:
image_dir = images
```
Where the first indicates the name of the database file located in the project root directory. The second variable `image_dir` indicates the folder in which the locally saved images are to be found.

Since images are referred in the database by their exact filename, all images can just be saved in a flat hierachy in the root of `image_dir`. This assumes that all filenames are globally unique.

### Migrate schema
Schema needs to be migrated using `alembic` whenever schematic changes occur, such as
a new table being added or columns being modified.

Migrations can be done from project root, using:
```
alembic revision --autogenerate
alembic upgrade head
```

### Configure
Set the path for the `*.db` SQLite file in the `alembic.ini` file. The syntax is folowing the [python configparser](https://docs.python.org/3.5/library/configparser.html).

### Usage
This module will create the database file given by `config.py` if it does not exists
once the library is imported.

**Example insertion:**
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
   tags          = ['protest', 'africa', 'example', 'test'],
   label         = .5
)
```

The above, will also make insertions into `Tags` table and link them to the image
through the `TaggedImages` table.

**Example filtering:**
```python
import protestDB.models as models

# Get list of all images with the tag 'protest':
protestTag = pc.getTag("protest")

protest_images = protestTag.images
```

Below is an example of printing out the number of images for each tag in the database.

**Example tag stats:**
```python
tags = pc.session.query(models.Tags).all()

for tag in tags:
    print("{:<15} {:d}".format(
        tag.tagName,
        len(tag.images))
    )
```

The above prints out a two column table where the first column has a fixed width of 15 and is left-aligned.

**Example show image:**
```python
t = pc.getTag("fire")
img = t.images[0]
img.show()
```

See the class `ProtestCursor` in the file protestDB.engine for
documentation on the possible parameters and their meaning.

## Serp Scraper

This code defines a commandline interface for scraping images.

### Get usage information:
```
python serp_driver.py --help
```
Otherwise the general idea is to provide a path to a directory where the images scraped will be saved, the key words to be scraped and the search engines (currently supports google and bing). Look in the help for additional arguments

### Limits
Bing has a limit of 210 images where google goes up to 800 in principle.

### Usage

Minimum arguments
```
python serp_driver.py images --key_words "jenifer anistion" "cats"
```

All arguments
```
python serp_driver.py images --sr google bing --key_words "jenifer anistion" "cats" --n_images 100 --timeout 10
```


## Serp Search terms scraper

This is a script built to automate multiple searches configured in a csv file in the following format:

| search_term | search_engine | n_images | label |
| ------------| :------------:| :------: | :---: |
| cats        | google        |  300     | 1     |
| dogs        | bing          |  332     | 0     |

Just pass the path to the csv file as an argument to the script

Attention: **When used, it will automatically add it to the db!!**