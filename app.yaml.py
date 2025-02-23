runtime: python39  # Python 3.9 のランタイムを指定

entrypoint: gunicorn -b :$PORT app:app  # Flask アプリケーションを gunicorn で起動

env_variables:
PS
C:\Users\otatu\my_flask_project > dir

ディレクトリ: C:\Users\otatu\my_flask_project

Mode
LastWriteTime
Length
Name
----                 -------------         ------ ----
d - ----        2024 / 12 / 31
10: 01
__pycache__
-a - ---        2024 / 12 / 31
10: 01
172
app.py

