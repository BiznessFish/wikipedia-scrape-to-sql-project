# wikipedia-scrape-to-sql-project
Example project of scraping data from wikipedia and storing it in a sqlite3 database

# Explanation

This is an example project to demonstrate web-scraping [a page on Wikipedia](https://en.wikipedia.org/wiki/Atlantic_hurricane_season). Let's say we are interested in getting all of the data for hurricanes that we have available, and want to store them in a SQL database.*

*A sqlite3 database is used in place of an actual database.

The HTML file provided was obtained using `curl`:

```curl -o hurricanes.html https://en.wikipedia.org/wiki/Atlantic_hurricane_season```

The Python script will create a .db file if there isn't one already there. A .sql script to create a table has been provided. If the idea is to create an empty .db file with one table, sqlite3 can do that.

To create the .db file, download the .sql script for creating a table.

First, make sure sqlite3 is installed. Then, run:

`sqlite3 hurricanes.db < hurricanes.sql`

The .sql script will run and create a .db file with a table called `atlantic_hurricanes`, without any entries.

Through the Python script, everything is auto-magically created with pandas. There is some added flexibility with this second method as you can insert rows without having to save things to Pandas, and allows for some finer control. 

The sql_queries.py file demonstrates how to run a SQL query using the scraped .db file.

Some notes on the parsing of this particular page:

- The HTML on the Wikipedia page when you look at inspect element for the Wikipedia page does not match up 100% with the HTML page obtained from curl/wget. There are some CSS classes that aren't there, and some tags that are missing. To understand the format you have to look at the obtained file. For example, getting all of the tables from the HTML file involved looking for the tag <table> and the class 'wikitable'.

- Since all of the tables have a different number of headers, the decision was made to scrape each of these tables into their own object, so that we have a lsit of all the tables.

- Some of these tables (specifically the ones at the end of the page), have a last summation row that includes the totals for the whole year for each column. These rows are actually tagged as table headers, which makes finding the row headers for these tables end up with many more headers than there actually are. Since these values are derived valeus and can be easily re-derived, we don't actually need them. When parsing the tables for each table, we can just stop once we reach "Total", which is the first cell of this summation row.

- Because of how hyperlinks are set-up on these tables, there are weird line breaks and spacing between the words of each header. For example, Number oftropical storms vs. Number of tropicalstorms. The easy solution is to just strip all of the newlines and spaces from the table header.

- The first table in the list is just a table of contents, so we can just ignore it when preprocessing.

- Certain tables contained rows that had all empty values. These were dropped.

- Some fields were moved into the Notes field. THey were added into the end of each Notes field preceded by what the field was and its associated value. For example, the Retired Names field was added into notes as "Retired Storm(s): [value]".

- Nearly all of the fields have all of the information that we need, except for damage and deaths. These required some preprocessing. When a cell had something like "Not Known" or "Unknown", the decision was made to make these into empty values. When there was "None" in the cell, they were replaced by 0, None and Null have different meanings! Some regexing was needed also to remove the "approximately" symbol and the "more than" symbols. So, if a field had 800+, it would just be 800, since there is n real way of knowing how much over 800 this number is, just taking it as the actual number is good enough.

- For damages, there were 'billions' and 'millions' instead of full entries of numbers. To fix this, they can all be replaced by "E9" or "E6", so that Python can understand them as scientific notation. The beginning numeric values with the decimal will thus be the coefficient. Some also had different symbols like > or ≥. All of the symbols were removed, as there really is no way to get a precise number on it. In using the scientific notation method, there will be some weird issues with the floating point precision, Python will have these as float64. An easy way to get around it is to just specify the datatype during the database creation in the script to round the numbers up or down.
