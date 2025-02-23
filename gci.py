# 必要なライブラリのインポート
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# 1. データの読み込み
train = pd.read_csv('C:/Users/otatu/Downloads/train.csv')  # 訓練データ
test = pd.read_csv('C:/Users/otatu/Downloads/test.csv')    # テストデータ

# 列名に空白が含まれていないか確認・除去
train.columns = train.columns.str.strip()
test.columns = test.columns.str.strip()

# 2. データの前処理
# 欠損値の補完
train['Age'].fillna(train['Age'].median(), inplace=True)
train['Embarked'].fillna(train['Embarked'].mode()[0], inplace=True)
test['Age'].fillna(test['Age'].median(), inplace=True)
test['Embarked'].fillna(test['Embarked'].mode()[0], inplace=True)

# カテゴリ変数のエンコーディング
train['Sex'] = train['Sex'].map({'male': 1, 'female': 0})
test['Sex'] = test['Sex'].map({'male': 1, 'female': 0})
train = pd.get_dummies(train, columns=['Embarked'])
test = pd.get_dummies(test, columns=['Embarked'])

# 家族の人数を特徴量に追加
train['FamilySize'] = train['SibSp'] + train['Parch']
test['FamilySize'] = test['SibSp'] + test['Parch']

# 交差項の生成
train['Pclass_Sex'] = train['Pclass'] * train['Sex']
train['Age_Fare'] = train['Age'] * train['Fare']
test['Pclass_Sex'] = test['Pclass'] * test['Sex']
test['Age_Fare'] = test['Age'] * test['Fare']

# 不要なカラムの削除
train.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)
test_ids = test['PassengerId']
test.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)

# 特徴量とターゲットの分割
X = train.drop('Perished', axis=1)
y = train['Perished']

# 訓練データと検証データに分割
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# データの標準化（MLPモデルで必要）
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
test_scaled = scaler.transform(test)

# テストデータの欠損値補完（テストデータの欠損値がエラーを引き起こすため）
test.fillna(test.median(), inplace=True)

# 3. 各モデルの訓練と評価
# 1) ロジスティック回帰
log_model = LogisticRegression(random_state=42)
log_model.fit(X_train_scaled, y_train)
log_pred = log_model.predict(X_val_scaled)
print("Logistic Regression Accuracy:", accuracy_score(y_val, log_pred))

# 2) ランダムフォレスト
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_val)
print("Random Forest Accuracy:", accuracy_score(y_val, rf_pred))

# 3) 多層パーセプトロン（MLP）
mlp_model = MLPClassifier(
    random_state=42,
    max_iter=1000,                   # イテレーション数を増加
    hidden_layer_sizes=(50, 50),     # 2層の隠れ層
    learning_rate_init=0.0005        # 学習率を調整
)
mlp_model.fit(X_train_scaled, y_train)
mlp_pred = mlp_model.predict(X_val_scaled)
print("MLP Accuracy:", accuracy_score(y_val, mlp_pred))

# 4. テストデータに対する予測と指定されたパスに提出用ファイルを保存
# ランダムフォレストモデルで予測
test_preds = rf_model.predict(test)

# 指定されたパスに保存
save_path = "C:/Users/otatu/Downloads/tax_calculation_result.csv"

# 提出用のDataFrame作成
submission = pd.DataFrame({'PassengerID': test_ids, 'Perished': test_preds})

# 指定されたパスにCSVファイルを上書き保存
submission.to_csv(save_path, index=False)
print(f"submission.csv has been saved to {save_path}")
