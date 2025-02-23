import pandas as pd
import numpy as np

# ファイルパス
lobstr_file = r'C:/Users/otatu/Downloads/payment_operations_2024-08-25.xls'  # 取引データのExcelファイルのパス
price_file = r'C:/Users/otatu/Downloads/xlm-usd-max.csv'  # 価格データのCSVファイルのパス
usd_jpy_file = r'C:/Users/otatu/Downloads/USD_JPY 過去データ (1).csv'  # ドル円のデータファイルのパス

# 1. データの読み込み
lobstr_df = pd.read_excel(lobstr_file)
price_df = pd.read_csv(price_file)
usd_jpy_df = pd.read_csv(usd_jpy_file, engine='python', header=0)  # ヘッダー行を正しく読み込む

# 2. 価格データの日付をdatetime型に変換し、タイムゾーンを削除して日足にリサンプリング
price_df['snapped_at'] = pd.to_datetime(price_df['snapped_at'], errors='coerce').dt.tz_localize(None).dt.normalize()
price_df_daily = price_df.resample('D', on='snapped_at').last().reset_index(drop=True)

# 3. ドル円データの日付をdatetime型に変換し、NaTを削除してから日足にリサンプリング
usd_jpy_df['日付け'] = pd.to_datetime(usd_jpy_df['日付け'], format='%Y/%m/%d', errors='coerce')
usd_jpy_df = usd_jpy_df.dropna(subset=['日付け'])
usd_jpy_df.set_index('日付け', inplace=True)
usd_jpy_df_daily = usd_jpy_df.resample('D').last().reset_index()
usd_jpy_df_daily = usd_jpy_df_daily.rename(columns={'日付け': 'DATE', '終値': 'usd_jpy'})

# 4. 'XLM' のみを含む取引をフィルタリング (YXLMを除外)
lobstr_df['AMOUNT'] = lobstr_df['AMOUNT'].astype(str)
xlm_transactions = lobstr_df[lobstr_df['AMOUNT'].str.contains(r'\bXLM\b', case=False, na=False)].copy()

# 'AMOUNT'列から数量と通貨を分割
split_data = xlm_transactions['AMOUNT'].str.split(' ', expand=True)
xlm_transactions['数量'] = split_data[0]
xlm_transactions['通貨'] = split_data[1]
xlm_transactions['数量'] = pd.to_numeric(xlm_transactions['数量'], errors='coerce')
xlm_transactions['通貨'] = xlm_transactions['通貨'].str.strip().str.upper()

# "DATE"列をdatetime型に変換し、日付部分のみを使用
xlm_transactions['DATE'] = pd.to_datetime(xlm_transactions['DATE'], errors='coerce').dt.normalize()

# 5. 月のフィルタリングを修正
# フィルタリング対象の月
months_to_include = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
xlm_transactions['month'] = xlm_transactions['DATE'].dt.strftime('%b')
filtered_transactions = xlm_transactions[xlm_transactions['month'].isin(months_to_include)]

# 受け取り('received')の取引のみを残す
filtered_transactions = filtered_transactions[
    filtered_transactions['TYPE'].str.contains('received', case=False, na=False)].copy()

# 日付の昇順（古い順）にソート
filtered_transactions = filtered_transactions.sort_values(by='DATE')

# 6. 価格データと取引データのマージ（取引データの日付と価格データの日付で）
merged_transactions = pd.merge(filtered_transactions, price_df_daily, left_on='DATE', right_on='snapped_at', how='left')

# ドル円の為替レートをマージ
merged_transactions = pd.merge(merged_transactions, usd_jpy_df_daily, on='DATE', how='left')

# マージ結果の確認
print("Merged DataFrame head after correcting:")
print(merged_transactions.head())

# 7. 日本円に換算し、移動平均法で平均取得単価を計算
total_cost = 0
total_quantity = 0
results = []

for index, row in merged_transactions.iterrows():
    quantity = row['数量']
    price_usd = row['price']
    exchange_rate = row['usd_jpy']  # ドル円レート
    if pd.notna(price_usd) and pd.notna(exchange_rate):
        price_jpy = price_usd * exchange_rate  # 日本円での価格

        if quantity > 0:
            total_cost += quantity * price_jpy
            total_quantity += quantity
            average_cost = total_cost / total_quantity

        results.append({
            '日付': row['DATE'],
            '取引量': quantity,
            '通貨': row['通貨'],
            '価格(USD)': price_usd,
            '為替レート': exchange_rate,
            '価格(JPY)': price_jpy,
            '保有総量': total_quantity,
            '平均取得単価(JPY)': average_cost
        })
    else:
        results.append({
            '日付': row['DATE'],
            '取引量': quantity,
            '通貨': row['通貨'],
            '価格(USD)': price_usd,
            '為替レート': exchange_rate,
            '価格(JPY)': np.nan,
            '保有総量': total_quantity,
            '平均取得単価(JPY)': np.nan
        })

# 結果をDataFrameに変換
results_df = pd.DataFrame(results)
results_df = results_df[['日付', '取引量', '通貨', '価格(USD)', '為替レート', '価格(JPY)', '保有総量', '平均取得単価(JPY)']]

# 日本語の列名でExcelに出力
output_file = r'C:/Users/otatu/Downloads/xlm_tax_calculation_spring_summer.xlsx'
with pd.ExcelWriter(output_file) as writer:
    results_df.to_excel(writer, sheet_name='取得単価計算結果', index=False)

print("計算結果が日本円でExcelに出力されました。")
