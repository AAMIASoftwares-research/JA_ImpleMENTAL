"""
READ ME :)

This is an example file to show how to read data from an sqlite3 database,
and how to add data to it as well starting from a pandas dataframe.
If needed, we have an utility function to convert a SAS database (sas7dbdat) to a
sqlite3 database through Pandas.

please install the following packages:
- pandas
with:
python -m pip install pandas

sqlite3 is part of the standard library of python, so you don't need to install it.

Please read along this file as if it were a small tutorial, and remember to change the
file paths in this file to your own file paths.
"""

# (Go Pogacar!!)

import pandas
import sqlite3

if __name__ == '__main__':
    # Fill in the path to your database (.sl3 file) here
    DATABASE_FILE_PATH = '/path/to/your/database/JA_database_example_Slovenia.sl3'
    DATABASE_FILE_PATH = 'C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ja_implemental_dashboard\\v1\\database\\example\\JA_database_example.sl3'

    # Create a connection to the database
    connection = sqlite3.connect(DATABASE_FILE_PATH)

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Read each table in the database and print the first 10 rows of each table
    list_of_tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    list_of_table_names = [table[0] for table in list_of_tables]
    for table_name in list_of_table_names:
        # get the column names and types
        columns = cursor.execute(f"PRAGMA table_info({table_name});").fetchall()
        column_names = [column[1] for column in columns]
        column_types = [column[2] for column in columns]
        print(f"\n{table_name}")
        print(column_names)
        print(column_types)
        # get the first 10 rows
        rows = cursor.execute(f"SELECT * FROM {table_name} LIMIT 10").fetchall()
        for row in rows:
            print(row)

    # Read the whole database into a pandas dataframe
    print("Pandas dataframe\n")
    for table_name in list_of_table_names:
        df = pandas.read_sql_query(f"SELECT * FROM {table_name};", connection)
        print(f"\n{table_name}")
        print(df.head(10))
    # Close the connection to the database
    print("\n\n\n")
    connection.close()


    # If you want to add data to the database, you can do it through pandas as well.
    # To create an sqlite3 database ex-novo, you can just convert your data to
    # for example CSV format or excel format, read the data with pandas, and export it to
    # the sqlite3 database with the to_sql method.
    # Here is an example from a CSV file with three columns: 'A', 'B', 'C'
    # containing 10 rows of random numbers (A), random letters (B), and random boolean values (C)
    # 
    # You can create your own tables in the preferred program/format, read them with pandas,
    # and translate them to the sqlite3 database with the to_sql method.
    example_csv_file = "C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ja_implemental_dashboard\\v1\\database\\example\\example_csv_table.csv"
    df = pandas.read_csv(
        example_csv_file,
        sep=',', # The separator used in the CSV file
        header=1,
        names=['A', 'B', 'C'],
        dtype={'A': int, 'B': str, 'C': bool},
    )
    print("Pandas dataframe from CSV\n")
    print(df.head())
    new_database_file_path = 'C:\\Users\\lecca\\Desktop\\AAMIASoftwares-research\\JA_ImpleMENTAL\\ja_implemental_dashboard\\v1\\database\\example\\example_database_from_csv.sl3'
    connection_new_database = sqlite3.connect(new_database_file_path)
    df.to_sql(
        "example_table",         # The name of the table in which to write the data 
        connection_new_database, # The connection to the database
        if_exists='replace',     # If the table already exists, replace it
        index=False
    )
    # now you can connect to the new database and read the data
    cursor_new_database = connection_new_database.cursor()
    results = cursor_new_database.execute("SELECT * FROM example_table WHERE C = 1;").fetchall()
    results = [r[0] for r in results]
    print("\nQuery results from the new database")
    print(results)

    # Hope this little guide was useful.
    # To install Sqlite3 on your system and use the command line interface
    # to work with it, you can follow this guide:
    # https://www.sqlite.org/
    # https://sqlite.org/fiddle/index.html
    # https://www.sqlite.org/quickstart.html
    # 
    # For the python package, you can find the documentation here:
    # https://docs.python.org/3/library/sqlite3.html




        
