import pandas as pd
import sqlite3
import os


def load_df_to_sqlite(df, db_name, table_name, project_root_dir="."):
    """
    Loads a pandas DataFrame into a specified SQLite database and table.

    Args:
        df (pd.DataFrame): The DataFrame to load.
        db_name (str): The name of the SQLite database file (e.g., 'laptops_analytics.db').
        table_name (str): The name of the table to create/replace in the database.
        project_root_dir (str): The root directory of the project, to ensure db is saved there.
    """
    if df is None:
        print("Error: DataFrame is None. Cannot load to SQLite.")
        return

    db_path = os.path.join(project_root_dir, db_name)

    try:
        conn = sqlite3.connect(db_path)
        print(f"Successfully connected to SQLite database: {db_path}")

        # Load the DataFrame into the SQLite table
        # if_exists='replace' will drop the table first if it exists and create a new one.
        # index=False will prevent pandas from writing DataFrame index as a column.
        df.to_sql(name=table_name, con=conn, if_exists='replace', index=False)

        print(f"Successfully loaded DataFrame into table '{table_name}' in database '{db_name}'.")

        # Verify by counting rows
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Table '{table_name}' now contains {count} rows.")

    except sqlite3.Error as e:
        print(f"SQLite error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print(f"SQLite connection to '{db_name}' closed.")