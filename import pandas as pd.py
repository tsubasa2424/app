import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# 訓練データの読み込み
train_df = pd.read_csv('"C:/Users/otatu/Downloads/train.csv"')
X = train_df.drop(columns=['TARGET'])
y = train_df['TARGET']

# データの前処理
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# モデルの学習
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_scaled, y)

# テストデータの読み込み
test_df = pd.read_csv('"C:/Users/otatu/Downloads/test.csv"')
X_test = test_df.drop(columns=['SK_ID_CURR'])
X_test_scaled = scaler.transform(X_test)

# 予測確率の出力
predictions = model.predict_proba(X_test_scaled)[:, 1]

# 提出ファイルの作成
submission = pd.DataFrame({
    'SK_ID_CURR': test_df['SK_ID_CURR'],
    'TARGET': predictions
})

submission.to_csv('submission.csv', index=False)