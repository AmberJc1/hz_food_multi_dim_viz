import pandas as pd
import sqlite3

class ShopDB:
    def __init__(self, db_path="restaurant.db"):
        self.conn = sqlite3.connect(db_path)

    def query_shop(self, district=None, cost_level=None):
        # 表名从 restaurant → shop
        sql = "SELECT * FROM shop WHERE 1=1 "
        params = []
        if district is not None:
            sql += " AND adname = ? "
            params.append(district)
        if cost_level is not None:
            sql += " AND cost_level = ? "
            params.append(cost_level)
        df = pd.read_sql(sql, self.conn, params=params)
        return df

    def stat_by_district(self):
        sql = "SELECT adname, COUNT(*) AS shop_count FROM shop GROUP BY adname"
        df = pd.read_sql(sql, self.conn)
        return df

    def close(self):
        self.conn.close()
