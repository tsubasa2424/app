import pandas as pd

# Paths to the Excel files
bitbank_file = r"C:\Users\otatu\Downloads\bitbank2.xlsx"
bitflyer_file = r"C:\Users\otatu\Downloads\bitflyer_xlm_calculation.xlsx"

# Load the two files
bitbank_df = pd.read_excel(bitbank_file)
bitflyer_df = pd.read_excel(bitflyer_file)

# Load new data (for 保有総量 and 平均取得単価)
new_data = {
    '取引日時': ['2023-09-29 00:00:00'],
    '数量': [568.1172594],
    '価格': [17.602],
    '保有総量': [568.1172594],
    '平均取得単価': [17.602]
}
new_df = pd.DataFrame(new_data)

# Add Missing Columns to File 2
bitflyer_df['注文ID'] = None
bitflyer_df['取引ID'] = None
bitflyer_df['通貨ペア'] = bitflyer_df['通貨']
bitflyer_df['タイプ'] = '成行'  # Assuming all are market orders
bitflyer_df['売/買'] = bitflyer_df['取引種別'].map({'買い': '買', '売り': '売り'})
bitflyer_df['数量'] = bitflyer_df['通貨1数量']
bitflyer_df['価格'] = bitflyer_df['取引価格']
bitflyer_df['手数料'] = bitflyer_df['手数料']
bitflyer_df['M/T'] = None  # No matching column found
bitflyer_df['取引日時'] = bitflyer_df['取引日時']

# Select the required columns and reorder them to match bitbank_df
bitflyer_df = bitflyer_df[['注文ID', '取引ID', '通貨ペア', 'タイプ', '売/買', '数量', '価格', '手数料', 'M/T', '取引日時']]

# Merge the two DataFrames
merged_df = pd.concat([bitbank_df, bitflyer_df])

# Add the new data with 保有総量 and 平均取得単価
merged_df['保有総量'] = None
merged_df['平均取得単価'] = None

# Concatenate the new_df with保有総量 and 平均取得単価
merged_df = pd.concat([merged_df, new_df])

# Convert the '取引日時' column to datetime format to avoid comparison issues
merged_df['取引日時'] = pd.to_datetime(merged_df['取引日時'], errors='coerce')

# Sort by '取引日時'
merged_df = merged_df.sort_values(by='取引日時')

# Save the merged DataFrame to a new Excel file
output_file = r"C:\Users\otatu\Downloads\merged_trades_with_average.xlsx"
merged_df.to_excel(output_file, index=False)

print(f"Merged file with new data saved to {output_file}")
