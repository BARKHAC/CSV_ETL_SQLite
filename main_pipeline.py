import os
import pandas as pd

# Import functions from our existing scripts
import download_dataset
from data_extraction import load_raw_data
from data_transformation import transform_laptop_data
from load_to_sqlite import load_df_to_sqlite

# Define constants for file paths and names
# Assuming this script is in laptop_etl_project, and other scripts are also there.
# The Kaggle download path is more complex, so we'll handle it in download_dataset.
# For simplicity in this main orchestrator, we'll assume download_dataset.py
# makes the CSV available at a known relative path or returns the path.

# Let's make download_dataset.py more robust by having it return the CSV path
# and creating a dedicated function there. For now, we'll use the hardcoded path
# as in data_extraction.py for the raw CSV, but ideally, this would be dynamic.

RAW_CSV_PARENT_DIR = os.path.expanduser("~/.cache/kagglehub/datasets/pradeepjangirml007/laptop-data-set/versions/1")
RAW_CSV_FILENAME = "laptop.csv"  # This is the known filename within the Kaggle download
RAW_CSV_FULL_PATH = os.path.join(RAW_CSV_PARENT_DIR, RAW_CSV_FILENAME)

TRANSFORMED_CSV_FILENAME = "transformed_laptops.csv"  # Saved in the project directory
DB_NAME = "laptops_analytics.db"  # Saved in the project directory
TABLE_NAME = "laptops_final"
PROJECT_ROOT_DIR = "."  # Relative to where this script is run (laptop_etl_project)


def run_download_step():
    """
    Placeholder for a more integrated download step.
    Currently, download_dataset.py is run manually or separately.
    A more robust implementation would have download_kaggle_dataset return the path.
    For now, we just check if the expected raw CSV exists.
    """
    print("--- Step 0: Dataset Download (Verification) ---")
    if not os.path.exists(RAW_CSV_FULL_PATH):
        print(f"ERROR: Raw dataset {RAW_CSV_FULL_PATH} not found.")
        print("Please ensure you have run download_dataset.py from kagglehub, or manually place it.")
        print("Alternatively, modify download_dataset.py to be callable and return the path.")
        # For now, we call the existing download_dataset.py's function
        # We need to modify download_dataset.py to have a callable function.
        # Let's assume download_kaggle_dataset() is defined in download_dataset.py
        # and it handles the download and prints the path.
        try:
            print("Attempting to run Kaggle dataset download...")
            # Capture the returned path (even if it's None)
            # The download_kaggle_dataset function is expected to print its own messages.
            confirmed_path = download_dataset.download_kaggle_dataset()

            if confirmed_path and os.path.exists(confirmed_path):
                # If download_kaggle_dataset confirms a path and it exists, we're good.
                # Potentially update RAW_CSV_FULL_PATH if dynamic paths are fully implemented.
                # For now, we assume confirmed_path IS RAW_CSV_FULL_PATH if not None.
                print(f"Raw dataset confirmed at: {confirmed_path}")
                return True  # Indicates success
            elif os.path.exists(RAW_CSV_FULL_PATH):
                # Fallback: if the fixed RAW_CSV_FULL_PATH exists, even if confirmed_path was None
                print(f"Raw dataset found/downloaded (verified by fixed path): {RAW_CSV_FULL_PATH}")
                return True
            else:
                print(
                    f"Download script ran, but dataset not found at expected path: {RAW_CSV_FULL_PATH} or via confirmation.")
                return False  # Explicitly return False
        except Exception as e:
            print(f"Error during download attempt: {e}")
            return False
    else:
        print(f"Raw dataset already exists: {RAW_CSV_FULL_PATH}")
        return True


def run_extraction_step(raw_csv_path):
    """Extracts data from the raw CSV file."""
    print("\n--- Step 1: Data Extraction ---")
    raw_df = load_raw_data(raw_csv_path)  # Use the function from data_extraction.py
    if raw_df is not None:
        print("Raw data loaded successfully.")
        raw_df.info()
    return raw_df


def run_transformation_step(raw_df):
    """Transforms the raw DataFrame."""
    print("\n--- Step 2: Data Transformation ---")
    transformed_df = transform_laptop_data(raw_df)
    if transformed_df is not None:
        print("Data transformed successfully.")
        # Save the transformed DataFrame to a CSV file
        transformed_csv_path = os.path.join(PROJECT_ROOT_DIR, TRANSFORMED_CSV_FILENAME)
        try:
            transformed_df.to_csv(transformed_csv_path, index=False)
            print(f"Successfully saved transformed data to {transformed_csv_path}")
        except Exception as e:
            print(f"Error saving transformed data to CSV: {e}")
            # We might still want to return the df for loading if saving fails for some reason
    return transformed_df


def run_load_step(transformed_df):
    """Loads the transformed DataFrame into SQLite."""
    print("\n--- Step 3: Data Loading ---")
    if transformed_df is not None:
        load_df_to_sqlite(transformed_df, DB_NAME, TABLE_NAME, project_root_dir=PROJECT_ROOT_DIR)
        print("Data loading process finished.")
    else:
        print("Skipping load step as transformed DataFrame is None.")


if __name__ == "__main__":
    print("===== Starting Laptop ETL Pipeline =====")

    # Step 0: Ensure dataset is downloaded
    # We need to modify download_dataset.py to be importable and have a function.
    # For now, let's adapt the main_pipeline to reflect this need.
    # The `run_download_step` will be a placeholder or a direct call if we modify download_dataset.py

    # Let's modify download_dataset.py first to make it callable.
    # For now, I will assume download_dataset.py has been modified to include:
    # def download_kaggle_dataset():
    #     import kagglehub
    #     path = kagglehub.dataset_download("pradeepjangirml007/laptop-data-set")
    #     print(f"Dataset downloaded to: {path}")
    #     # We need to ensure RAW_CSV_FULL_PATH is consistent with this path.
    #     # This is tricky because kagglehub creates versioned folders.
    #     # A better approach is for download_kaggle_dataset to *return* the exact CSV path.
    # For this iteration, run_download_step primarily verifies existence.

    if not run_download_step():
        print("Halting pipeline due to missing raw dataset.")
    else:
        # Step 1: Extraction
        # The current data_extraction.py has its own CSV_FILE_PATH.
        # We should modify load_raw_data to accept a path.
        # Let's assume load_raw_data in data_extraction.py is modified:
        # def load_raw_data(csv_filepath): ...
        df_raw = run_extraction_step(RAW_CSV_FULL_PATH)

        if df_raw is not None:
            # Step 2: Transformation
            df_transformed = run_transformation_step(df_raw)

            if df_transformed is not None:
                # Step 3: Load
                run_load_step(df_transformed)
            else:
                print("Halting pipeline because transformation failed.")
        else:
            print("Halting pipeline because extraction failed.")

    print("\n===== Laptop ETL Pipeline Finished =====") 