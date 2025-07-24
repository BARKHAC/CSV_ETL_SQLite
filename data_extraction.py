import pandas as pd

CSV_FILE_PATH = r'C:\Users\bchai\.cache\kagglehub\datasets\pradeepjangirml007\laptop-data-set\versions\1\laptop.csv'

def load_laptop_data(csv_filepath):
    try:
        df = pd.read_csv(csv_filepath)
        print(f"Successfully loaded {csv_filepath}")
        return df
    except FileNotFoundError:
        print(f"Error: The file was not found at {csv_filepath}")
        return None
    except Exception as e:
        print(f"An error occured while loading the file: {e}")
        return None

if __name__ == "__main__":
    laptop_df = load_laptop_data(CSV_FILE_PATH)

    if laptop_df is not None:
        print("\n--DataFrame info--")
        laptop_df.info()
        print("\n--First 5 rows of DataFrame--")
        print(laptop_df.head())