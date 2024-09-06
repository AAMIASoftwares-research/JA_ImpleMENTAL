import os
import random, numpy
import sqlite3

# create/connect to a database
database_name = __file__.replace('.py', '.db')
db = sqlite3.connect(database_name)
cursor = db.cursor()

# populate the database with 1000 rows of the following columns:
# ID_SUBJECT: random text of 5 characters from a list of 100 possibile combinations
# DATE_DIAG: random date between 2015 and 2019
cursor.execute('CREATE TABLE IF NOT EXISTS data (ID_SUBJECT TEXT, DATE_DIAG DATE)')
cursor.execute('DELETE FROM data')
for i in range(1000):
    ID_SUBJECT = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
    DATE_DIAG = f"{random.randint(2015, 2019)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    cursor.execute('INSERT INTO data (ID_SUBJECT, DATE_DIAG) VALUES (?, ?)', (ID_SUBJECT, DATE_DIAG))
print("total rows: ", cursor.execute('SELECT COUNT(*) FROM data').fetchone()[0])
print("distinct id_subject: ", cursor.execute('SELECT COUNT(DISTINCT ID_SUBJECT) FROM data').fetchone()[0])

# print 30 random rows
print("30 random rows: ", cursor.execute("SELECT CAST(strftime('%Y', DATE_DIAG) AS INTEGER) FROM data WHERE CAST(strftime('%Y', DATE_DIAG) AS INTEGER) BETWEEN 2016 AND 2019 LIMIT 30").fetchall())


# select, for each individual subject, the minimum date of diagnosis (only the year)
cursor.execute('CREATE TABLE IF NOT EXISTS min_date (ID_SUBJECT TEXT, MIN_DATE INTEGER, NUM_OCCURRENCES INTEGER)')
cursor.execute('DELETE FROM min_date')
cursor.execute("INSERT INTO min_date (ID_SUBJECT, MIN_DATE, NUM_OCCURRENCES) SELECT ID_SUBJECT, MIN(CAST(strftime('%Y', DATE_DIAG) AS INTEGER)), COUNT(*) FROM data GROUP BY ID_SUBJECT")
print("total rows min date: ", cursor.execute('SELECT COUNT(*) FROM min_date').fetchone()[0])
# get one subject with more than one occurrence
id_subject = cursor.execute('SELECT ID_SUBJECT FROM min_date WHERE NUM_OCCURRENCES > 1 LIMIT 1').fetchone()[0]
print(f"Subject {id_subject} has more than one occurrence at: {cursor.execute('SELECT DATE_DIAG FROM data WHERE ID_SUBJECT = ? ORDER BY DATE_DIAG', (id_subject,)).fetchall()}, minimum date is {cursor.execute('SELECT MIN_DATE FROM min_date WHERE ID_SUBJECT = ?', (id_subject,)).fetchone()}")

