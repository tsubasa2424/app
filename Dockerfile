# ベースイメージとしてPython 3.8を使用
FROM python:3.8

# コンテナ内での作業ディレクトリを設定
WORKDIR /app

# Pythonの依存パッケージをインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ローカルのPythonコードをコンテナにコピー
COPY . .

# コンテナ起動時に実行されるコマンドを指定
CMD ["python", "main.py"]
