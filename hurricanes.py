from bs4 import BeautifulSoup
import pandas as pd

# Make an empty list of Dataframes so we can put DataFrames into it
dfs = []

# Open the provided .html file scraped from the Wikipedia page
with open('hurricanes.html', 'r') as f:
    contents = f.read()

    # Use the html parser from BeautifulSoup
    soup = BeautifulSoup(contents, 'html.parser')

    # This find_all command scrapes all of the tags that have the table tag,
    # having a css class of 'wikitable', which is Wikipedia's specific table type
    # In other words, we're getting a list of tables!

    tables = soup.find_all('table', {'class': 'wikitable'})

    # Make each table into its own DataFrame
    for table in tables:

        # Make a list for each column name/header
        headers = []

        for th in table.find_all('th'):

            # Some tables have the bottom-most 'Totals' row as a table header
            # for some reason. This part is to stop
            # appending headers once we get to the 'Totals'
            if th.text.strip('\n') == "Total":
                break

            # Tiny bit of pre-processing to strip away newlines and spaces.
            headers.append(th.text.strip('\n').replace(' ',''))

        # Make a list for all of the rows
        rows = []
        table_rows = table.find_all('tr')

        # Adding table rows from each table as a row
        for row in table_rows:
            td = row.find_all('td')
            row = [row.text.strip('\n') for row in td]
            rows.append(row)

        df = pd.DataFrame(rows, columns=headers)
        dfs.append(df)

# We don't need the first table -- it's the table of contents table that doesn't actually
# hold any data
dfs = dfs[1:]

# Concatenating all of the tables together.
df_merged = pd.concat(dfs)

# Resetting index after performing concatenation
df_merged.reset_index(drop=True, inplace=True)

# Drop any rows that don't have any entries in them -- Some may have gotten through
df_merged.dropna(inplace=True, how='all')

# This data is quite dirty. We can clean them here.
# First let's combine the columns that need to be combined
df_merged['Notes'] = (df_merged['Notes'] + '. Strongest Storm(s): ' + df_merged['Strongeststorm']
                      + '. Retired Storm(s): ' + df_merged['Retirednames'])

# Now that we have the columns we're keeping, we can drop the columns we don't need
# tropical cyclones
df_merged.drop(columns= (['ACE', 'Numberoftropicalcyclones',
                          'Strongeststorm', 'Retirednames', 'Majorlandfallhurricanes']), inplace=True)

# We should rename the columns of the Dataframe so that they're easier to work with
df_merged.columns = ['year', 'tropical_storms', 'hurricanes', 'major_hurricanes',
                     'deaths', 'notes', 'damage']

# Actually, these columns should be in a different order
# We can easily reorder the columns we want like this
ordered_column_names = ['year', 'tropical_storms', 'hurricanes', 'major_hurricanes',
                     'deaths', 'damage', 'notes']
df = df_merged[ordered_column_names].copy()

# Next we start cleaning the data. Let's start by converting integers to integers
numeric_column_names = ['year', 'tropical_storms', 'hurricanes', 'major_hurricanes']
df[numeric_column_names] = df[numeric_column_names].apply(pd.to_numeric,
                                                          downcast='signed', errors='coerce')

# Since deaths and damage are special, we can use some regexing to clean them.
# We can investigate which of these do not match numbers.

# The very first row is empty. There are several that are either "Not known" or "Unknown".
# Several also have "None". One has "Numerous". There are also some that give imprecise
# values for the number of deaths. Several have weird +, >, ~, or ,.
# We will first start by replacing the empty row and "None" rows with 0.
df['deaths'].replace(r'(^$)|None', 0, regex=True, inplace=True)

# Replace the ones that are not known and unknown with NaN. Since we don't have an actual
# count for the "Numerous" cell, we should replace this one with empty values as well
df['deaths'].replace(r'Not known|Unknown|Numerous', '', regex=True, inplace= True)

# Remove all non number symbols
df['deaths'].replace(r'>|~|\+|,', '', regex=True, inplace=True)

# Turn it into an integer type
# Some of these will have Nans, which prevents us from turning it into an integer, since
# NaN is a float. Another option is to code it as -1 to keep everything consistently
# an integer.
df.deaths = pd.to_numeric(df.deaths, errors='raise')

# Now we can begin cleaning damage. Let's first replace all of the "Unknown" with NaN, since
# we're missing that information
df['damage'].replace(r'Unknown', None, regex=True, inplace= True)

# Remove the funky symbols in front and inside
df['damage'].replace(r'≥|\$|\s|>|\+|,', '', regex=True, inplace= True)

# We can turn millions and billions into scientific notation so to_numeric can
# interpret them as numerics
multipliers = {'million':'E6', 'billion':'E9'}
df['damage'].replace(multipliers, regex=True, inplace= True)

df.damage = pd.to_numeric(df.damage, errors='coerce')

# Now all of our data is cleansed and ready to be dumped into a .db file

import sqlite3
from sqlite3 import Error

conn = None
try:
    conn = sqlite3.connect('hurricanes.db')
    sqlite_table = "atlantic_hurricanes"

    # Needed a solution here to round off float64 numbers which was giving weird precisions
    # I preferred this solution as it was a little cleaner. Here we are  specifying the datatypes
    # for these specific fields, as they were having some trouble.

    df.to_sql(sqlite_table, conn, dtype={'damage': 'DECIMAL(10,5)', 'deaths': 'DECIMAL(10,5)'},
              if_exists='replace')

except Error as e:
    print(e)
finally:
    if conn:
        conn.close()