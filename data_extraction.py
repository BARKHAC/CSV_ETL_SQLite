import pandas as pd
from data_transformation import transform_laptop_data
# Import the SQLite loading function
from load_to_sqlite import load_df_to_sqlite


CSV_FILE_PATH = r'C:\Users\bchai\.cache\kagglehub\datasets\pradeepjangirml007\laptop-data-set\versions\1\laptop.csv'


def load_raw_data(csv_filepath):
    """Loads the raw laptop data from the specified CSV file path."""
    try:
        df = pd.read_csv(csv_filepath)
        print(f"Successfully loaded {csv_filepath}")
        return df
    except FileNotFoundError:
        print(f"Error: The file was not found at {csv_filepath}")
        return None
    except Exception as e:
        print(f"An error occurred while loading the file: {e}")
        return None

if __name__ == "__main__":
    raw_laptop_df = load_raw_data(CSV_FILE_PATH)

    if raw_laptop_df is not None:
        print("\n--- Raw DataFrame Info ---")
        raw_laptop_df.info()
        # print("\n--- First 5 Rows of Raw DataFrame ---")
        # print(raw_laptop_df.head())

        # Apply transformations
        print("\n--- Applying Transformations ---")
        transformed_laptop_df = transform_laptop_data(raw_laptop_df)

        if transformed_laptop_df is not None:
            print("\n--- Transformed DataFrame Info (after first few transformations) ---")
            transformed_laptop_df.info()
            print("\n--- First 5 Rows of Transformed DataFrame (after first few transformations) ---")
            print(transformed_laptop_df.head())
            # You can add more inspection printouts here, e.g.:
            # print("\n--- Basic Descriptive Statistics ---")
            # print(transformed_laptop_df.describe(include='all'))
            # print("\n--- Missing Values Per Column ---")
            # print(transformed_laptop_df.isnull().sum())

            # Save the transformed DataFrame to a CSV file
            output_path = "transformed_laptops.csv" # Save in the current project directory
            try:
                transformed_laptop_df.to_csv(output_path, index=False)
                print(f"\nSuccessfully saved transformed data to {output_path}")

                # Now, load the transformed DataFrame into SQLite
                print("\n--- Loading Transformed Data to SQLite Database ---")
                db_name = "laptops_analytics.db"  # Database will be in the project directory
                table_name = "laptops_final"
                load_df_to_sqlite(transformed_laptop_df, db_name, table_name)

            except Exception as e:
                print(f"\nError saving transformed data to CSV or loading to SQLite: {e}")
