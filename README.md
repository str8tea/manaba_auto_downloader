# Manaba Auto-downloader
※このプログラムの実行には、manabaのアカウントが必須です！

---

# OverView
manabaというクラウド型教育支援システムから講義資料を自動でダウンロードするプログラムです。   
このプログラムを実行すると、Chromeブラウザが起動し、manabaのホームページに移動してスクレイピングを行います。そのスクレイピングした情報をもとに講義資料をダウンロードします。
 
# Features
 
このプログラムを実行すると、講義資料を自動でダウンロードしてくれるため、講義前にmanabaにアクセスして講義資料をダウンロードする手間が省けます。
 
# Requirement
言語
* Python 3.10.2

必要なライブラリ
* beautifulsoup4 4.10.0
* selenium 4.2.0
* webdriver-manager 3.5.2

その他
* manabaのログイン情報（ユーザIDやパスワードなど）が保存されているChromeのユーザーデータ  
（manabaに自動ログインできるユーザーデータ）

# Installation
 
```bash
pip install beautifulsoup4
pip install selenium
pip install webdriver-manager
```

もしくは、クローンした後
```bash
pip install -r requirements.txt
```
 
# Usage

1. 下記のコマンドを実行して、クローンする
```bash
git clone https://github.com/str8tea/manaba_auto_downloader.git
```
2. manabaのログイン情報が保存されているChromeのユーザーデータを用意する
1. settings.jsonを編集して各種設定を行う（参照：settings.json.example）
1. download_content_list.jsonに自動でダウンロードしたい講義資料の講義の名前とコンテンツの名前を指定する（参照：download_content_list.json.example）
1. manaba_auto_downloaderディレクトリに移動する
1. 下記のコマンドを実行して、プログラムを実行する
```bash
python manaba_auto_downloader\apps\apps.py
```
 
# Note

このプログラムの実行には、manabaのログイン情報が保存されているChromeのユーザーデータが必要です。 また、作者が通っている大学のmanabaでしか動作は保証されません。

 
