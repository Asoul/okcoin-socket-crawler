# OKCoin Websocket Crawler

一個串接 okcoin websocket 的小爬蟲，把資料存到 MySQL，附上 supervisor 腳本可以長期開在伺服器上。

<p align="center">
  <img src="https://raw.githubusercontent.com/Asoul/okcoin-socket-crawler/master/img/okcoin.png"></img>
</p>

## 基本需求

- Python3
- MySQL
- virtualenv (用 pip 裝)

## 安裝

```
# 建立虛擬環境
virtualenv -p `which python3` venv

# 使用虛擬環境
. venv/bin/activate

# 安裝相關套件
pip install -r requirements.txt

# 建立資料庫 (假設使用者為 root)
mysql -u root -e "CREATE DATABASE okcoin_future"

# 更改 alembic.ini 和 server.py 中的 db URL，設定資料庫的使用者、密碼 (Optional)
vim alembic.ini
vim server.py

# 建立資料庫欄位
alembic upgrade head
```

## 執行

```
python server.py
```

## 利用 supervisor 背景執行 (長時間放置在伺服器上)

```
# 安裝 supervisor
sudo apt-get install -y supervisor

# 更改 supervisor 中的路徑位置，設定資料夾目錄和輸出 log 目錄 (Optional)
vim supervisor/okcoin-socket-crawler.conf

# 新增 supervisor 腳本
sudo cp ./supervisor/okcoin-socket-crawler.conf /etc/supervisor/conf.d/

# 讀取腳本
sudo supervisorctl reread

# 更新腳本
sudo supervisorctl update

# 執行 supervisor
sudo supervisorctl start okcoin-socket-crawler
```

# Contribution

有任何想法都歡迎發 PR、開 issue，或與我聯絡 `azx754@gmail.com`。

# License
MIT

# Donation

BTC 錢包: `3QB4Liv4Yp1ttpHnk8DT135juhKTBEWDc7`

<p align="center">
  <img src="https://raw.githubusercontent.com/Asoul/okcoin-socket-crawler/master/img/qrcode.png"></img>
</p>
