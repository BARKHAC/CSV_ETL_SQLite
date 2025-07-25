import pandas as pd
import numpy as np  # numpy might be useful for more complex transformations or NaN handling
import re  # For more complex regex later if needed


def parse_storage_capacity(storage_str):
    """Helper function to parse storage strings (e.g., '512 GB SSD Storage', '1 TB HDD', 'No HDD') into GB."""
    storage_str = str(storage_str).lower()
    if 'no hdd' in storage_str or 'no ssd' in storage_str or not any(char.isdigit() for char in storage_str):
        return 0

    capacity = 0
    # Look for TB first
    tb_match = re.search(r'(\d+\.?\d*)\s*tb', storage_str)
    if tb_match:
        capacity = float(tb_match.group(1)) * 1024  # Convert TB to GB
    else:
        # Look for GB if TB not found
        gb_match = re.search(r'(\d+\.?\d*)\s*gb', storage_str)
        if gb_match:
            capacity = float(gb_match.group(1))
        else:
            # If no units but digits are present, assume GB as a fallback (might need adjustment)
            num_match = re.search(r'(\d+\.?\d*)', storage_str)
            if num_match:
                capacity = float(num_match.group(1))

    return int(capacity)  # Return as integer GB


def extract_processor_brand(name_str):
    name_str = str(name_str).lower()
    if 'intel' in name_str or 'celeron' in name_str or 'pentium' in name_str:
        return 'Intel'
    if 'amd' in name_str or 'ryzen' in name_str or 'athlon' in name_str:
        return 'AMD'
    if 'apple' in name_str or 'm1' in name_str or 'm2' in name_str:
        return 'Apple'
    if 'mediatek' in name_str:
        return 'MediaTek'
    if 'qualcomm' in name_str or 'snapdragon' in name_str:
        return 'Qualcomm'
    return None  # Or 'Other'


def extract_processor_series(name_str):
    name_str = str(name_str).lower()
    # Apple M series - prioritize as it's distinct
    apple_m_match = re.search(r'(m[123])(?:\s*(pro|max|ultra))?', name_str)
    if apple_m_match:
        series = apple_m_match.group(1)
        modifier = apple_m_match.group(2)
        return f"{series.upper()}{f' {modifier.capitalize()}' if modifier else ''}"

    # Intel Core series - look for 'core' followed by iX or ultra X
    core_match = re.search(r'core\s+(i[3579]|ultra\s*[3579]|m[357])', name_str)
    if core_match:
        return f"Core {core_match.group(1).replace(' ', '')}"  # e.g. Core i5, Core ultra7

    # AMD Ryzen series - look for 'ryzen' followed by a digit
    ryzen_match = re.search(r'ryzen\s+([3579]|threadripper)', name_str)
    if ryzen_match:
        return f"Ryzen {ryzen_match.group(1)}"  # e.g. Ryzen 5, Ryzen 7

    # Simpler generic Intel checks (if not Core but still Intel, like Pentium, Celeron)
    if 'celeron' in name_str:
        return 'Celeron'
    if 'pentium' in name_str:
        return 'Pentium'
    if 'intel' in name_str and 'xeon' in name_str:  # Intel Xeon
        return 'Xeon'

    # Simpler AMD checks (if not Ryzen but still AMD, like Athlon)
    if 'athlon' in name_str:
        return 'Athlon'

    if 'mediatek' in name_str:
        mtk_match = re.search(r'mediatek\s*([^\s(]+)', name_str)
        if mtk_match and mtk_match.group(1) not in ['octa-core', 'quad-core', 'dual-core']:
            return f"MediaTek {mtk_match.group(1).capitalize()}"
        return "MediaTek"  # Fallback for general Mediatek

    if 'snapdragon' in name_str:
        snap_match = re.search(r'snapdragon\s*([^\s(]+)', name_str)
        if snap_match:
            return f"Snapdragon {snap_match.group(1)}"
        return "Snapdragon"

    return None


def extract_processor_generation(name_str):
    name_str = str(name_str).lower()

    # Pattern 1: (XXth Gen), (XXnd Gen), etc. explicitly in parentheses or standing alone
    gen_match_explicit = re.search(r'(?:\(|\b)(\d{1,2})(?:st|nd|rd|th)\s*gen(?:eration)?(?:\)|\b)', name_str)
    if gen_match_explicit:
        return f"{gen_match_explicit.group(1)}th Gen"

    # Pattern 2: For Intel model numbers like iX-YYYY or iX YYYY or iX-YYY or iX YYY
    # e.g., i5-1240P -> 12th, i7-8550U -> 8th, i5 1035G1 -> 10th
    # Intel Core i5 (12th Gen)
    intel_gen_series_match = re.search(r'(?:core\s*)?i([3579])(?:-|\s)(\d{1,2})\d{2,3}',
                                       name_str)  # for iX-GGxx or iX-Gxxx (G=Gen)
    if intel_gen_series_match:
        gen_prefix = intel_gen_series_match.group(2)  # This is the potential generation part
        try:
            gen_num = int(gen_prefix)
            if len(intel_gen_series_match.group(
                    1)) == 1 and 1 <= gen_num <= 19:  # e.g. i5-12345 -> 12th gen, i7-8xxx -> 8th gen
                return f"{gen_num}th Gen"
        except ValueError:
            pass

    # Handle cases like "Intel Core i5 12th Gen" where it might not be in parens
    # This is partly covered by gen_match_explicit but with more context
    intel_named_gen = re.search(r'intel\s+core\s+i[3579]\s+(\d{1,2})(?:st|nd|rd|th)\s+gen', name_str)
    if intel_named_gen:
        return f"{intel_named_gen.group(1)}th Gen"

    # AMD Ryzen X000 series (e.g., Ryzen 5 5600H -> 5th Gen (by convention of 1st digit of model no))
    # Ryzen 7 5800H -> 5 (so 5th gen)
    # Ryzen 9 7940HS -> 7 (so 7th gen)
    amd_ryzen_gen_match = re.search(r'ryzen\s+[3579]\s+(\d)\d{3}', name_str)
    if amd_ryzen_gen_match:
        gen_digit = amd_ryzen_gen_match.group(1)
        # Common Ryzen generations by first model digit
        # 1xxx, 2xxx, 3xxx, 4xxx(laptop), 5xxx, 6xxx(laptop), 7xxx
        if gen_digit in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return f"{gen_digit}xxx Series Gen"  # Not strictly 'th' gen but a series indicator

    return None


def extract_core_info(name_str):
    name_str = str(name_str).lower()
    core_match = re.search(r'(dual|quad|hexa|octa|deca)[-\s]*core', name_str)
    if core_match:
        return f"{core_match.group(1).capitalize()}-Core"
    return None


def transform_laptop_data(df_raw):
    """Applies various cleaning and transformation steps to the raw laptop DataFrame."""
    # Make a copy to avoid modifying the original DataFrame in place
    df = df_raw.copy()

    print("Starting data transformation...")

    # 1. Drop 'Unnamed: 0' column
    if 'Unnamed: 0' in df.columns:
        df.drop('Unnamed: 0', axis=1, inplace=True)
        print("- Dropped 'Unnamed: 0' column.")

    # 2. Clean RAM column
    # Expecting formats like "8 GB RAM", "16GB", etc.
    if 'RAM' in df.columns:
        df['RAM_GB'] = df['RAM'].astype(str).str.upper()  # Convert to string and uppercase
        df['RAM_GB'] = df['RAM_GB'].str.replace(r'\s*GB\s*RAM', '', regex=True)  # Remove " GB RAM"
        df['RAM_GB'] = df['RAM_GB'].str.replace(r'\s*GB', '', regex=True)  # Remove " GB"
        df['RAM_GB'] = df['RAM_GB'].str.extract(r'(\d+)')  # Extract digits
        df['RAM_GB'] = pd.to_numeric(df['RAM_GB'], errors='coerce')  # Convert to numeric, errors become NaN
        # df.drop('RAM', axis=1, inplace=True) # Optional: drop original RAM column
        print("- Cleaned 'RAM' column into 'RAM_GB' (numeric).")

    # 3. Clean Ghz column
    # Expecting formats like "2.1 Ghz", "3.0 Ghz Max", "1.8GHz"
    if 'Ghz' in df.columns:
        df['Processor_Speed_GHz'] = df['Ghz'].astype(str).str.lower()  # Convert to string and lowercase
        # Extract the first floating point or integer number found
        df['Processor_Speed_GHz'] = df['Processor_Speed_GHz'].str.extract(r'(\d+\.?\d*)')
        df['Processor_Speed_GHz'] = pd.to_numeric(df['Processor_Speed_GHz'], errors='coerce')
        # df.drop('Ghz', axis=1, inplace=True) # Optional: drop original Ghz column
        print("- Cleaned 'Ghz' column into 'Processor_Speed_GHz' (numeric).")

    # 4. Clean SSD Column
    if 'SSD' in df.columns:
        df['SSD_Capacity_GB'] = df['SSD'].apply(parse_storage_capacity)
        print("- Cleaned 'SSD' column into 'SSD_Capacity_GB' (numeric GB).")

    # 5. Clean HDD Column
    if 'HDD' in df.columns:
        df['HDD_Capacity_GB'] = df['HDD'].apply(parse_storage_capacity)
        print("- Cleaned 'HDD' column into 'HDD_Capacity_GB' (numeric GB).")

    # 6. Clean Adapter Column
    if 'Adapter' in df.columns:
        df['Adapter_Wattage'] = df['Adapter'].astype(str).str.lower()
        df['Adapter_Wattage'] = df['Adapter_Wattage'].str.replace(r'watt', '', regex=False)  # remove "watt"
        df['Adapter_Wattage'] = df['Adapter_Wattage'].str.replace(r'w', '', regex=False)  # remove "w"
        df['Adapter_Wattage'] = df['Adapter_Wattage'].str.strip()
        # Extract leading digits, coerce non-numeric to NaN
        df['Adapter_Wattage'] = pd.to_numeric(df['Adapter_Wattage'], errors='coerce')
        print("- Cleaned 'Adapter' column into 'Adapter_Wattage' (numeric).")

    # 7. Clean Battery_Life Column
    if 'Battery_Life' in df.columns:
        df['Battery_Life_Hours'] = df['Battery_Life'].astype(str).str.lower()
        # Extract the first number (integer or float) found
        df['Battery_Life_Hours'] = df['Battery_Life_Hours'].str.extract(r'(\d+\.?\d*)')
        df['Battery_Life_Hours'] = pd.to_numeric(df['Battery_Life_Hours'], errors='coerce')
        print("- Cleaned 'Battery_Life' column into 'Battery_Life_Hours' (numeric).")

    # 8. Drop original columns that have been transformed
    columns_to_drop = ['RAM', 'Ghz', 'SSD', 'HDD', 'Adapter', 'Battery_Life']
    existing_cols_to_drop = [col for col in columns_to_drop if col in df.columns]
    if existing_cols_to_drop:
        df.drop(columns=existing_cols_to_drop, axis=1, inplace=True)
        print(f"- Dropped original columns: {', '.join(existing_cols_to_drop)}.")

    # --- Feature Engineering ---
    print("\nStarting feature engineering...")

    # 9. Refine Processor_Brand and Engineer Processor Features
    if 'Processor_Name' in df.columns:
        df['Processor_Brand_Cleaned'] = df['Processor_Name'].apply(extract_processor_brand)
        # Overwrite original Processor_Brand if it exists, or use the new one
        df['Processor_Brand'] = df['Processor_Brand_Cleaned']
        df.drop('Processor_Brand_Cleaned', axis=1, inplace=True)
        print("- Refined 'Processor_Brand'.")

        df['Processor_Series'] = df['Processor_Name'].apply(extract_processor_series)
        print("- Engineered 'Processor_Series'.")
        df['Processor_Generation'] = df['Processor_Name'].apply(extract_processor_generation)
        print("- Engineered 'Processor_Generation'.")
        df['Processor_Core_Info'] = df['Processor_Name'].apply(extract_core_info)
        print("- Engineered 'Processor_Core_Info'.")

    # 10. Engineer Display_Size_Inches
    if 'Display' in df.columns:
        # Attempt to extract a number, assuming it's inches.
        # This regex looks for numbers, possibly with a decimal, that might be followed by ' inch' or '\"'
        # More robustly extract the first number sequence found, assuming it is the display size.
        df['Display_Size_Inches'] = df['Display'].astype(str).str.extract(r'^\s*(\d+\.?\d*)')
        df['Display_Size_Inches'] = pd.to_numeric(df['Display_Size_Inches'], errors='coerce')
        # df.drop('Display', axis=1, inplace=True) # Optional: drop original Display column
        print("- Engineered 'Display_Size_Inches' from 'Display' column.")

    # 11. Engineer Price_Range
    if 'Price' in df.columns:
        # Define price bins and labels
        # Adjust bins according to actual price distribution for better categorization
        price_bins = [0, 30000, 60000, 90000, np.inf]
        price_labels = ['Budget', 'Mid-Range', 'Upper Mid-Range', 'Premium']
        df['Price_Range'] = pd.cut(df['Price'], bins=price_bins, labels=price_labels, right=False)
        print("- Engineered 'Price_Range'.")

    print("\nTransformation steps applied so far:")
    print(df.info())
    print("\nSample of transformed data (first 5 rows):")
    print(df.head())

    return df