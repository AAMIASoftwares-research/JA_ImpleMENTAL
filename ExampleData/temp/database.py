import os
import random, numpy
import sqlite3


# test: create a database with table 'data' which contains column 'ID_SUBJECT' and 'TYPE_INT'
# ID_SUBJECT is a random string of length N that can reoccur,
# TYPE_INT is an integer between 0 and 7 inclusive
file = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        "databaseb2.db"
    )
)
conn = sqlite3.connect(file)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS data (ID_SUBJECT TEXT, TYPE_INT INTEGER)')
c.execute('DELETE FROM data')
#fill
for i in range(5000):
    ID_SUBJECT = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=random.randint(3,4)))
    TYPE_INT = random.randint(0, 7)
    c.execute('INSERT INTO data (ID_SUBJECT, TYPE_INT) VALUES (?, ?)', (ID_SUBJECT, TYPE_INT))
c.execute("SELECT COUNT(DISTINCT ID_SUBJECT) FROM data")
print(c.fetchone()[0])
# now, what i want is, for each distint ID_PATIENT, count how many times it
# appears in the table
# I want to do this in a single query with GROUP BY if possible
c.execute("SELECT ID_SUBJECT, COUNT(*) FROM data GROUP BY ID_SUBJECT")
r = c.fetchall()
r.sort(key=lambda x: x[1], reverse=True)
print(r[:50])

# close and quit
conn.commit()
c.close()
conn.close()












quit()



# test database slovenia
file = "C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ExampleData\\Slovenia\\JA_Implemental-sample_v3.sqlite3"
#file = "C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ExampleData\\Dati QUADIM - Standardizzati - Sicilia\\DATABASE.sqlite3"

db = sqlite3.connect(file)
cursor = db.cursor()
tables = [a[0] for a in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("tables: ", tables)
print("temp tables: ", cursor.execute("SELECT name FROM sqlite_temp_master WHERE type='table'").fetchall())


for table in tables:
    print("Table", table, f"({cursor.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]}) entries")
    names = [a[1] for a in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
    types = [a[2] for a in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
    for n, t in zip(names, types):
        print(f"  {n} ({t})")
    print("- Some rows:")
    rows = cursor.execute(f"SELECT * FROM {table} ORDER BY RANDOM() LIMIT 5").fetchall()
    for row in rows:
        print(f"  {row}")
db.close()

if 0:
    # FOR BLAZ
    # create example database from our database with randomized ID_SUBJECT in each table
    in_file = "C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ExampleData\\Dati QUADIM - Standardizzati - Sicilia\\DATABASE.jasqlite3"
    out_file = os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "Slovenia",
            'example_database.sqlite3'
        )
    )
    # of the in database, we copy 1000 rows of tables:
    # - 'demographics'
    # - 'pharma'
    # - 'diagnoses'
    # - 'interventions'
    # - 'physical_exams'
    db = sqlite3.connect(in_file)
    cursor = db.cursor()
    db.execute('ATTACH DATABASE ? AS out', (out_file,))
    cursor.execute('CREATE TABLE IF NOT EXISTS out.demographics AS SELECT * FROM demographics LIMIT 1000')
    cursor.execute('CREATE TABLE IF NOT EXISTS out.pharma AS SELECT * FROM pharma LIMIT 1000')
    cursor.execute('CREATE TABLE IF NOT EXISTS out.diagnoses AS SELECT * FROM diagnoses LIMIT 1000')
    cursor.execute('CREATE TABLE IF NOT EXISTS out.interventions AS SELECT * FROM interventions LIMIT 1000')
    cursor.execute('CREATE TABLE IF NOT EXISTS out.physical_exams AS SELECT * FROM physical_exams LIMIT 1000')
    # now, modify the ID_SUBJECT in each table to be a random string of 5 to 9 characters and numbers
    choice = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz'
    for table in ['demographics', 'pharma', 'diagnoses', 'interventions', 'physical_exams']:
        for rowid in range(1, 1001):
            ID_SUBJECT = ''.join(random.choices(choice, k=random.randint(5, 9)))
            cursor.execute(f"UPDATE out.{table} SET ID_SUBJECT = ? WHERE rowid = ?", (ID_SUBJECT, rowid))
    db.commit()
    print("database created!")
    cursor.execute("DETACH DATABASE out")
    cursor.close() 
    db.close()

quit()





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





# create another table named 'ast' with columns named 'ast_<i>' of type TEXT where i is a number between 1 and 40
# fill it with NULL values for n_rows rows
print("\n\nAST ------------------")
n_rows = 1000
n_columns = 20
cursor.execute('CREATE TABLE IF NOT EXISTS ast (' + ', '.join([f'ast_{i} INTEGER DEFAULT NULL' for i in range(1, n_columns+1)]) + ')')
cursor.execute('DELETE FROM ast')
for i in range(n_rows):
    cursor.execute('INSERT INTO ast DEFAULT VALUES')
print("total rows ast: ", cursor.execute('SELECT COUNT(*) FROM ast').fetchone()[0])
# ast_<i> values:
ast_1_values = [20, 40, 50, 1, 44]
ast_2_values = [40, 30, 20, 10]
ast_3_values = [i for i in range(14)]
# fill in these values in the respective columns
# so that column ast_1 has values 20, 40, 50, 1, 44, NULL, NULL, NULL, ....
# and column ast_2 has values 40, 30, 20, 10, NULL, NULL, NULL, NULL, ....
for i, value in enumerate(ast_1_values):
    cursor.execute(f'UPDATE ast SET ast_1 = ? WHERE rowid = ?', (value, i+1))
print("ast_1 values: ", cursor.execute('SELECT ast_1 FROM ast LIMIT 20').fetchall())
# now, let's imagine that ast_2_values are taken from a different table instead of a python variable
# - build the table ast_2_values with 30 rows and 1 column named 'value' with values chosen from ast_2_values
cursor.execute('CREATE TABLE IF NOT EXISTS ast_2_values (value INTEGER)')
cursor.execute('DELETE FROM ast_2_values')
import numpy
v_ = numpy.random.choice(ast_2_values, 30, replace=True)
for i, value in enumerate(v_):
    cursor.execute('INSERT INTO ast_2_values (value) VALUES (?)', (int(value),))
print("ast_2_values: ", cursor.execute('SELECT * FROM ast_2_values').fetchall())
# - now, in ast column ast_2, replace the first NULL values with the distinct values from ast_2_values
#   so that, if distinct values of ast_2_values.value are 40, 30, 20, 10, the first 4 NULL values in ast_2
#   become 40, 30, 20, 10
# basically i want to update the first values of ast_2 so that they match exactly the sorted distinct values of ast_2_values
# the following query does the job, but it is not recursive
cursor.execute("""
    CREATE TEMPORARY TABLE values_distinct_sorted AS
    SELECT DISTINCT value FROM ast_2_values ORDER BY value
""")
cursor.execute("""
    UPDATE ast SET ast_2 = (
        SELECT value
        FROM values_distinct_sorted
        WHERE rowid = ast.rowid
    )
""")
cursor.execute("DROP TABLE temp.values_distinct_sorted")



print("ast_2: ", cursor.execute('SELECT ast_2 FROM ast LIMIT 20').fetchall())

