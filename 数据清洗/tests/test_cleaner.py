import sys
from pathlib import Path

# 将项目根目录加入Python导入搜索路径
BASE_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from src.feature_engineering import generate_features
from src.database import ShopDB

TEST_CSV = BASE_DIR / "data/processed/hangzhou_feature.csv"

def test_feature_columns():
    """测试特征工程是否成功生成cost_level、score_level字段"""
    try:
        df = pd.read_csv(str(TEST_CSV), encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(str(TEST_CSV), encoding="gbk")

    df_new = generate_features(df)
    # 校验新增字段存在
    assert "cost_level" in df_new.columns
    assert "score_level" in df_new.columns
    print("测试通过：成功生成消费等级、评分等级字段")
def test_db_query():
    """测试数据库查询接口正常可用"""
    db = ShopDB()
    res = db.query_shop(district="上城区")
    assert res is not None
    print("测试通过：数据库筛选接口正常运行")

def test_stat_function():
    """测试统计接口返回数据不为空"""
    db = ShopDB()
    stat_df = db.stat_by_district()
    assert len(stat_df) > 0
    print("测试通过：区域统计接口正常运行")

if __name__ == "__main__":
    test_feature_columns()
    test_db_query()
    test_stat_function()
    print("\n全部用例执行成功！")
