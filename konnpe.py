import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

# データの読み込み
train_df = pd.read_csv("C:/Users/otatu/Downloads/train.csv")

# カラム名を表示して、'TARGET' カラムの存在を確認
print("カラム名:", train_df.columns)

# TARGETカラムが存在するか確認
if 'TARGET' not in train_df.columns:
    print("TARGETカラムが見つかりません。")
else:
    # 特徴量とターゲットの分割
    X = train_df.drop(columns=['TARGET'])
    y = train_df['TARGET']

    # データを訓練データとテストデータに分割
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # ランダムフォレストモデルの作成
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # テストデータでの予測
    y_pred = model.predict_proba(X_test)[:, 1]

    # AUCスコアの計算
    auc_score = roc_auc_score(y_test, y_pred)
    print(f"AUCスコア: {auc_score:.4f}")
