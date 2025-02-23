import pandas as pd
import chardet


# エンコーディングの自動検出関数
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']


# GMOのファイルパス
gmo_file = r'C:/Users/otatu/Downloads/gmo2023_trading_report.csv'

# 1. GMOのデータ読み込み (エンコーディングを自動検出)
gmo_encoding = detect_encoding(gmo_file)
gmo_df = pd.read_csv(gmo_file, encoding=gmo_encoding, engine='python', header=0)
gmo_df['DATE'] = pd.to_datetime(gmo_df['日時'], format='%Y/%m/%d %H:%M', errors='coerce').dt.normalize()

# 2. XLMの取引のみをフィルタリング
gmo_df = gmo_df[gmo_df['銘柄名'] == 'XLM']
gmo_df = gmo_df[['DATE', '約定数量', '約定レート']].rename(columns={'約定数量': 'xlm', '約定レート': 'price_jpy'})

# 3. 平均取得単価の計算
total_cost = 0
total_quantity = 0
results_gmo = []

for index, row in gmo_df.iterrows():
    quantity = row['xlm']
    price_jpy = row['price_jpy']

    if pd.notna(price_jpy):
        total_cost += quantity * price_jpy
        total_quantity += quantity
        average_cost = total_cost / total_quantity

        results_gmo.append({
            '日付': row['DATE'],
            '取引量': quantity,
            '価格(JPY)': price_jpy,
            '保有総量': total_quantity,
            '平均取得単価(JPY)': average_cost
        })

# 4. 結果をDataFrameに変換して保存
results_df_gmo = pd.DataFrame(results_gmo)
results_df_gmo = results_df_gmo[['日付', '取引量', '価格(JPY)', '保有総量', '平均取得単価(JPY)']]

output_file_gmo = r'C:/Users/otatu/Downloads/gmo_xlm_calculation.xlsx'
with pd.ExcelWriter(output_file_gmo) as writer:
    results_df_gmo.to_excel(writer, sheet_name='取得単価計算結果', index=False)

print("GMOの計算結果が日本円でExcelに出力されました。")
