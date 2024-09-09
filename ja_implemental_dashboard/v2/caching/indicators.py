import os
import sqlite3
import json
from .caching import get_cache_folder
from ..database.database import get_all_tables

def get_indicators_cache_database_file() -> str:
    """ Get the path to the cache file that is a database file for indicators
    calls that have already been computed.
    """
    cache_fname = "indicators.cache.sqlite3"
    cache_file = os.path.normpath(
        os.path.join(get_cache_folder(), cache_fname)
    )
    return cache_file

def initialize_indicators_cache_database(force:bool=False) -> None:
    """ Initialize the indicators cache database.
    """
    cache_file = get_indicators_cache_database_file()
    if os.path.exists(cache_file) and not force:
        return
    conn = sqlite3.connect(cache_file)
    tables = get_all_tables(conn)
    c = conn.cursor()
    if len(tables) > 0:
        for t in tables:
            c.execute("DELETE FROM ?;", (t,))
            c.execute("DROP TABLE IF EXISTS ?;", (t,)) 
    
    c.execute(
        """
        CREATE TABLE indicators (
            indicator_name TEXT PRIMARY KEY,
            indicator_value REAL
        )
        """
    )
    conn.commit()
    conn.close()

def get_table_name_for_indicator(indicator_name:str, create_if_not_exist:bool=False) -> str:
    """ Get the table name for the indicator.
    """
    table_name = f"indicator_{indicator_name}"
    if create_if_not_exist:
        cache_file = get_indicators_cache_database_file()
        conn = sqlite3.connect(cache_file)
        c = conn.cursor()
        c.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                call_signature TEXT PRIMARY KEY,
                x_json TEXT,
                y_json TEXT
            )
            """
        )
        conn.commit()
        conn.close
    return table_name

def get_table_columns_for_indicator() -> list:
    """ Get the columns for the table for the indicator.
    """
    return ["call_signature", "x_json", "y_json"]

def get_call_signature_text(
    disease_code:str,
    age_interval:list[tuple[int,int]],
    gender:str,
    civil_status:str,
    job_condition:str,
    educational_level:str,
    cohort:str|None=None,
) -> str:
    """ Get the call signature based on the input arguments.
    """
    age_interval_ = sorted(age_interval, key=lambda x: x[0] + 0.001*x[1])
    list_ = [disease_code]
    if cohort is not None:
        list_.append(cohort)
    list_.extend(
        [
            "_".join([f"({a[0]}-{a[1]})" for a in age_interval_]),
            gender,
            civil_status,
            job_condition,
            educational_level
        ]
    )
    call_signature = "_".join(list_)
    return str(call_signature)

