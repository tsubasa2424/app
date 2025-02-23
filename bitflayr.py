import pandas as pd

# Excelファイルの読み込み
file_path = r"C:\Users\otatu\Downloads\ビットバンクつばさ.xlsx"
df = pd.read_excel(file_path)

# 取引日時で古い順に並び替え
df['取引日時'] = pd.to_datetime(df['取引日時'])
df = df.sort_values(by='取引日時')

# 不要な列を削除
df = df.drop(columns=['取引ID', '注文ID', 'タイプ', 'M/T'])

# 必要な列を並び替え
columns = ['取引日時'] + [col for col in df.columns if col != '取引日時']
df = df[columns]

# 計算用のリストを初期化
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

# 初期値を設定
total_quantity_bought = 0
total_quantity_sold = 0
total_purchase_value = 0
total_sales_value = 0
average_acquisition_price = 0
cumulative_profit = 0
cumulative_loss = 0
cumulative_tax_due = 0

# 日にちごとに集計と計算を行う
for index, row in df.iterrows():
    if row['売/買'] == '買':
        # 買いの計算
        daily_quantity_bought = row['数量']
        total_quantity_bought += daily_quantity_bought
        total_purchase_value += row['数量'] * row['価格']
        average_acquisition_price = total_purchase_value / total_quantity_bought
        daily_sales_value = 0
        daily_profit_loss = 0
        daily_tax_due = 0
    else:
        # 売りの計算
        daily_quantity_bought = 0
        total_quantity_sold += row['数量']
        daily_sales_value = row['数量'] * row['価格']
        total_sales_value += daily_sales_value

        # 利益/損失の計算
        sales_proceeds = daily_sales_value
        acquisition_cost = average_acquisition_price * row['数量']
        daily_profit_loss = sales_proceeds - acquisition_cost

        # 累計利益と損失を更新
        if daily_profit_loss > 0:
            cumulative_profit += daily_profit_loss
        else:
            cumulative_loss += daily_profit_loss

        # 税額を計算
        tax_rate = 0.20
        daily_tax_due = max(0, daily_profit_loss) * tax_rate
        cumulative_tax_due += daily_tax_due

    # リストに追加
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

# 結果をExcelファイルに保存
output_path = r"C:\Users\otatu\Downloads\xlm_tax_calculation_combined_recalculated_with_sales_and_tax.fixed.xlsx"
df.to_excel(output_path, index=False)

print("計算が完了しました。結果は次のファイルに保存されています：", output_path)
