import pandas as pd
import numpy as np

# ファイルパスのリストを直接指定
file_paths = [
    r'C:/Users/otatu/Downloads/papabitbank2024.csv',
    r'C:/Users/otatu/Downloads/papabitbank2023.csv',
    r'C:/Users/otatu/Downloads/papabitbank2022.csv',
    r'C:/Users/otatu/Downloads/papabitbank2021.csv',
    r'C:/Users/otatu/Downloads/papabit2020.csv',
    r'C:/Users/otatu/Downloads/papabitbank2019.csv',
    r'C:/Users/otatu/Downloads/papabitbank2018.csv',
    r'C:/Users/otatu/Downloads/papabitbank2017.csv'
]

# 1. データの読み込みと結合
dfs = []
for file_path in file_paths:
    df = pd.read_csv(file_path, engine='python', header=0)
    dfs.append(df)

# データを結合
if dfs:
    bitbank_df = pd.concat(dfs, ignore_index=True)
else:
    print("ファイルが見つかりませんでした。")
    exit()

# 2. 価格データと為替データの読み込み
price_file = r'C:/Users/otatu/Downloads/xlm-usd-max.csv'  # 価格データのCSVファイルのパス
usd_jpy_file = r'C:/Users/otatu/Downloads/USD_JPY 過去データ (1).csv'  # ドル円のデータファイルのパス

price_df = pd.read_csv(price_file)
usd_jpy_df = pd.read_csv(usd_jpy_file, engine='python', header=0)

# 3. 価格データの日付をdatetime型に変換し、タイムゾーンを削除して日足にリサンプリング
price_df['snapped_at'] = pd.to_datetime(price_df['snapped_at'], errors='coerce').dt.tz_localize(None).dt.normalize()
price_df_daily = price_df.resample('D', on='snapped_at').last().reset_index(drop=True)

# 4. ドル円データの日付をdatetime型に変換し、NaTを削除してから日足にリサンプリング
usd_jpy_df['日付け'] = pd.to_datetime(usd_jpy_df['日付け'], format='%Y/%m/%d', errors='coerce')
usd_jpy_df = usd_jpy_df.dropna(subset=['日付け'])
usd_jpy_df.set_index('日付け', inplace=True)
usd_jpy_df_daily = usd_jpy_df.resample('D').last().reset_index()
usd_jpy_df_daily = usd_jpy_df_daily.rename(columns={'日付け': 'DATE', '終値': 'usd_jpy'})

# 5. XLM の取引データを日付順にソート
bitbank_df['DATE'] = pd.to_datetime(bitbank_df['日付'], format='%Y/%m/%d', errors='coerce').dt.normalize()
bitbank_df = bitbank_df.sort_values(by='DATE')

# 6. 価格データと取引データのマージ（取引データの日付と価格データの日付で）
merged_transactions = pd.merge(bitbank_df[['DATE', 'xlm']], price_df_daily, left_on='DATE', right_on='snapped_at',
                               how='left')

# ドル円の為替レートをマージ
merged_transactions = pd.merge(merged_transactions, usd_jpy_df_daily, on='DATE', how='left')

# 7. 日本円に換算し、保有枚数が増えた日に平均取得単価を計算
total_cost = 0
total_quantity = 0
previous_quantity = 0
results = []

for index, row in merged_transactions.iterrows():
    current_quantity = row['xlm']
    price_usd = row['price']
    exchange_rate = row['usd_jpy']  # ドル円レート

    if pd.notna(price_usd) and pd.notna(exchange_rate):
        price_jpy = price_usd * exchange_rate  # 日本円での価格

        # 保有枚数の変動を確認
        if current_quantity > previous_quantity:
            added_quantity = current_quantity - previous_quantity
            total_cost += added_quantity * price_jpy
            total_quantity += added_quantity
            average_cost = total_cost / total_quantity
        else:
            average_cost = total_cost / total_quantity if total_quantity > 0 else np.nan

        previous_quantity = current_quantity

        results.append({
            '日付': row['DATE'],
            '取引量': current_quantity,
            '価格(USD)': price_usd,
            '為替レート': exchange_rate,
            '価格(JPY)': price_jpy,
            '保有総量': total_quantity,
            '平均取得単価(JPY)': average_cost
        })
    else:
        results.append({
            '日付': row['DATE'],
            '取引量': current_quantity,
            '価格(USD)': price_usd,
            '為替レート': exchange_rate,
            '価格(JPY)': np.nan,
            '保有総量': total_quantity,
            '平均取得単価(JPY)': np.nan
        })

# 8. 結果をDataFrameに変換してExcelに出力
results_df = pd.DataFrame(results)
results_df = results_df[['日付', '取引量', '価格(USD)', '為替レート', '価格(JPY)', '保有総量', '平均取得単価(JPY)']]

output_file = r'C:/Users/otatu/Downloads/xlm_tax_calculation_bitbank_8_years.xlsx'
with pd.ExcelWriter(output_file) as writer:
    results_df.to_excel(writer, sheet_name='取得単価計算結果', index=False)

print("計算結果が日本円でExcelに出力されました。")
