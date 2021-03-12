import sqlite3
from sqlite3 import Error

conn = None
try:
    conn = sqlite3.connect('hurricanes.db')

    # Needed a solution here to round off float64 numbers which was giving weird precisions
    # I preferred this solution as it was a little cleaner. Here we are  specifying the datatypes
    # for these specific fields, as they were having some trouble.

    query = conn.execute('SELECT * FROM atlantic_hurricanes')
    print(query.fetchall())

except Error as e:
    print(e)
finally:
    if conn:
        conn.close()