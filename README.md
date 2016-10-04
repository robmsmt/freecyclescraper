# freecyclescraper
Scrapes all the freecycle pages you put in a list and displays them in a single searchable and sortable table. Will detect new posts and use MacOSX speech to alert you to them.

## How to Install

1. install python 3.4
2. `pip install beautifulsoup4`
3. `pip install html5lib` (optional if you want to use basic html.parser)
4. `pip install reqests`
4. run `python freecyclescraper.py`
5. start simplehttp server to serve with `python -m SimpleHTTPServer`
6. access from localhost:8000

Depending on your setup you may need to use `pip3` and `python3` commands.

## Todo

~~1. fix AJAX loading of changed JSON data rather than JS refreshing page~~
2. add log/db of all freecycle posts to do long term data analysis
3. improve new post detection by using unique postID rather than posts that x number of minutes old.
4. improve regex implemenation, it is hacky, posts descriptions with "|" or locations with ")" will probably break displaying
