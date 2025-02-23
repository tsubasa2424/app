import pandas as pd

# Excelファイルの読み込み
file_path = r"C:\Users\otatu\Downloads\bitbank2024.xlsx"
df = pd.read_excel(file_path)

# 取引日時で古い順に並び替え
df['取引日時'] = pd.to_datetime(df['取引日時'])
df = df.sort_values(by='取引日時')

# 取引ID、注文ID、タイプ、M/T、手数料を削除
df = df.drop(columns=['取引ID', '注文ID', 'タイプ', 'M/T'])

# 必要な列を左に移動
columns = ['取引日時'] + [col for col in df.columns if col != '取引日時']
df = df[columns]

# 2023年12月31日時点の累積データを設定 (例：average_acquisition_priceを28.85、initial_quantityを2023年の保有総量として設定)
average_acquisition_price = 28.85
initial_quantity = 19646.99  # 2023年末の保有総量を設定してください
total_quantity_bought = initial_quantity
total_purchase_value = average_acquisition_price * initial_quantity

# 2024年の計算に必要な変数の初期化
total_quantity_sold = 0
total_sales_value = 0
cumulative_profit = 0
cumulative_loss = 0
cumulative_tax_due = 0

# 各列に対応するリストを用意
total_quantity_bought_list = []
total_quantity_sold_list = []
average_acquisition_price_list = []
total_purchase_value_list = []
daily_sales_value_list = []
total_sales_value_list = []
daily_profit_loss_list = []
cumulative_profit_list = []
cumulative_loss_list = []
daily_tax_due_list = []
cumulative_tax_due_list = []
daily_quantity_bought_list = []

# 日にちごとに集計と計算を行う
for index, row in df.iterrows():
    if row['売/買'] == '買':
        # 買いの合計を計算
        daily_quantity_bought = row['数量']
        total_quantity_bought += daily_quantity_bought
        total_purchase_value += row['数量'] * row['価格']
        average_acquisition_price = total_purchase_value / total_quantity_bought
        daily_sales_value = 0  # 購入時は売却値を0に設定
        daily_profit_loss = 0  # 購入時は利益/損失も0に設定
        daily_tax_due = 0  # 購入時は税額も0に設定
    else:
        # 売りの合計を計算
        daily_quantity_bought = 0  # 売却時は買い合計枚数は0
        total_quantity_sold += row['数量']
        daily_sales_value = row['数量'] * row['価格']
        total_sales_value += daily_sales_value  # 売りの合計金額を足す

        # 利益/損失を計算
        sales_proceeds = daily_sales_value
        acquisition_cost = average_acquisition_price * row['数量']
        daily_profit_loss = sales_proceeds - acquisition_cost

        if daily_profit_loss > 0:
            cumulative_profit += daily_profit_loss
        else:
            cumulative_loss += daily_profit_loss  # 負の値として減算

        # 税金を計算（利益が出た場合）
        tax_rate = 0.20
        daily_tax_due = max(0, daily_profit_loss) * tax_rate
        cumulative_tax_due += daily_tax_due

    # 各計算結果をリストに追加
    total_quantity_bought_list.append(total_quantity_bought)
    total_quantity_sold_list.append(total_quantity_sold)
    average_acquisition_price_list.append(average_acquisition_price)
    total_purchase_value_list.append(total_purchase_value)
    daily_sales_value_list.append(daily_sales_value)
    total_sales_value_list.append(total_sales_value)
    daily_profit_loss_list.append(daily_profit_loss)
    cumulative_profit_list.append(cumulative_profit)
    cumulative_loss_list.append(cumulative_loss)
    daily_tax_due_list.append(daily_tax_due)
    cumulative_tax_due_list.append(cumulative_tax_due)
    daily_quantity_bought_list.append(daily_quantity_bought)

# 計算結果をデータフレームに追加
df['買いの合計枚数'] = daily_quantity_bought_list
df['合計購入枚数'] = total_quantity_bought_list
df['保有総量'] = df['合計購入枚数'] - total_quantity_sold_list
df['買いの合計金額'] = total_purchase_value_list
df['平均取得単価'] = average_acquisition_price_list
df['その日の売り金額'] = daily_sales_value_list
df['売りの合計枚数'] = total_quantity_sold_list
df['売りの合計金額'] = total_sales_value_list
df['利益/損失'] = daily_profit_loss_list
df['合計利益'] = cumulative_profit_list
df['合計損失'] = cumulative_loss_list
df['税額'] = daily_tax_due_list
df['合計税額'] = cumulative_tax_due_list

# 結果を新しいExcelファイルに保存
output_path = r"C:\Users\otatu\Downloads\xlm_tax_calculation_combined_recalculated_with_sales_and_tax.all.xlsx"
df.to_excel(output_path, index=False)

print("計算が完了しました。結果は次のファイルに保存されています：", output_path)
