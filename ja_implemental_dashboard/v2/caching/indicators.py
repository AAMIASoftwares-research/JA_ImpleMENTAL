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
            c.execute(f"DELETE FROM {t};")
            c.execute(f"DROP TABLE IF EXISTS {t};") 
    # Thye following 'indicators' table will not be used anywhere, it exists just
    # to initialize the database file
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

def is_call_in_cache(
    indicator_name:str,
    disease_code:str,
    age_interval:list[tuple[int,int]],
    gender:str,
    civil_status:str,
    job_condition:str,
    educational_level:str,
    cohort:str|None=None,
) -> bool:
    """ Check if the call is in the cache.
    """
    cache_file = get_indicators_cache_database_file()
    if not os.path.exists(cache_file):
        initialize_indicators_cache_database(force=True)
    table_name = get_table_name_for_indicator(indicator_name, create_if_not_exist=True)
    call_signature = get_call_signature_text(
        disease_code=disease_code,
        age_interval=age_interval,
        gender=gender,
        civil_status=civil_status,
        job_condition=job_condition,
        educational_level=educational_level,
        cohort=cohort
    )
    conn = sqlite3.connect(cache_file)
    c = conn.cursor()
    c.execute(
        f"SELECT COUNT(*) FROM {table_name} WHERE call_signature = ?",
        (call_signature,)
    )
    count = int(c.fetchone()[0])
    conn.commit()
    conn.close()
    return count > 0

def retrieve_cached_json(indicator_name:str,
    disease_code:str,
    age_interval:list[tuple[int,int]],
    gender:str,
    civil_status:str,
    job_condition:str,
    educational_level:str,
    cohort:str|None=None,
) -> tuple[str,str]:
    """ Retrieve the cached JSON data.
    Before calling this fucntion, you have to be sure
    that the call is in the cache.
    Check it with the function is_call_in_cache.

    Returns:
        x_json, y_json
    """
    cache_file = get_indicators_cache_database_file()
    if not os.path.exists(cache_file):
        initialize_indicators_cache_database(force=True)
    conn = sqlite3.connect(cache_file)
    c = conn.cursor()
    table_name = get_table_name_for_indicator(indicator_name)
    call_signature = get_call_signature_text(
        disease_code=disease_code,
        age_interval=age_interval,
        gender=gender,
        civil_status=civil_status,
        job_condition=job_condition,
        educational_level=educational_level,
        cohort=cohort
    )
    c.execute(
        # there should not be more than one row with the same call signature
        f"SELECT x_json, y_json FROM {table_name} WHERE call_signature = ? LIMIT 1",
        (call_signature,)
    )
    x_json, y_json = c.fetchone()
    conn.close()
    return x_json, y_json

def cache_json(
    indicator_name:str,
    disease_code:str,
    age_interval:list[tuple[int,int]],
    gender:str,
    civil_status:str,
    job_condition:str,
    educational_level:str,
    x_json:str,
    y_json:str,
    cohort:str|None=None,
) -> None:
    """ Cache the JSON data.
    """
    cache_file = get_indicators_cache_database_file()
    if not os.path.exists(cache_file):
        initialize_indicators_cache_database(force=True)
    conn = sqlite3.connect(cache_file)
    c = conn.cursor()
    table_name = get_table_name_for_indicator(indicator_name, create_if_not_exist=True)
    call_signature = get_call_signature_text(
        disease_code=disease_code,
        age_interval=age_interval,
        gender=gender,
        civil_status=civil_status,
        job_condition=job_condition,
        educational_level=educational_level,
        cohort=cohort
    )
    c.execute(
        f"INSERT INTO {table_name} (call_signature, x_json, y_json) VALUES (?, ?, ?)",
        (call_signature, str(x_json), str(y_json))
    )
    conn.commit()
    conn.close()
    
