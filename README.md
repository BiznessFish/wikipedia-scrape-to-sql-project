# wikipedia-scrape-to-sql-project
Example project of scraping data from wikipedia and storing it in a sqlite3 database

# Explanation

This is an example project to demonstrate web-scraping from Wikipedia. A sqlite3 database is used in place of a database connection.

The HTML file provided was obtained using `curl`:

```curl -o hurricanes.html https://en.wikipedia.org/wiki/Atlantic_hurricane_season```

The Python script will create a .db file if there isn't one already there. A .sql script to create a table has been provided. If the idea is to create an empty .db file with one table, sqlite3 can do that.

To create the .db file, download the .sql script for creating a table.

First, make sure sqlite3 is installed. Then, run:

`sqlite3 hurricanes.db < hurricanes.sql`

The .sql script will run and create a .db file with a table called `atlantic_hurricanes`, without any entries.

Through the Python script, everything is auto-magically created with pandas. There is some added flexibility with this second method as you can insert rows without having to save things to Pandas, and allows for some finer control. 

The sql_queries.py file demonstrates how to run a SQL query using the scraped .db file.
