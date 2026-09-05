# scripts/init_database.py
import sqlite3
import pandas as pd
from pathlib import Path

# scripts文件夹向上一级 = 项目根目录
BASE_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = BASE_DIR / "restaurant.db"
CSV_PATH = BASE_DIR / "data/processed/hangzhou_feature.csv"

if __name__ == "__main__":
    # 编码容错读取csv
    try:
        df = pd.read_csv(str(CSV_PATH), encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(str(CSV_PATH), encoding="gbk")

    db_conn = sqlite3.connect(str(DB_PATH))
    df.to_sql("shop", db_conn, if_exists="replace", index=False)
    db_conn.close()

    print(f"数据库写入路径：{DB_PATH}")
    print(f"数据表 shop 导入完成，共 {len(df)} 条商家记录")
