倒出安裝環境
$ pip freeze > requirements.txt

安裝 package
$ pip install -r requirements.txt

第一次執行失敗，no such machine
$ python init_db.py 

執行檔案
$ flask run

打包應用
$ pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" --add-data "icon.jpg;." app.py


