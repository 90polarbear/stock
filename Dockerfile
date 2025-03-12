# 使用 Python 3.11 的 slim 版本作為基礎映像，減少映像大小
FROM python:3.11-slim

# 安裝系統依賴，用於編譯 TA-Lib
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz \
    && apt-get clean

# 設定工作目錄
WORKDIR /app

# 複製項目文件到容器中
COPY . /app

# 安裝 Python 依賴
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 指定啟動命令
CMD ["gunicorn", "app:app"]
