# OKCOIN Websocket Crawler

一個串接 okcoin websocket 的小爬蟲，把資料存到 MySQL，附上 supervisor 腳本可以長期開在伺服器上。

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

# 建立資料庫
mysql -u root -e "CREATE DATABASE okcoin_future"

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

# 新增 supervisor 腳本
sudo cp ./supervisor/okcoin-socket-crawler.conf /etc/supervisor/conf.d/

# 讀取腳本
sudo supervisorctl reread

# 更新腳本
sudo supervisorctl update

# 執行 supervisor
sudo supervisorctl start okcoin-socket-crawler
```
