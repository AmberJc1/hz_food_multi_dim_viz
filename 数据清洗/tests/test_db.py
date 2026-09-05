# test_db.py
from src.database import ShopDB

db = ShopDB()
# 测试筛选上城区平价餐厅
print(db.query_shop(district="上城区", cost_level="平价").head())
# 测试区域统计
print(db.stat_by_district())
