# src/feature_engineering.py
import pandas as pd
import numpy as np

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    df_out = df.copy()

    # ========== 1.消费等级 cost_level ==========
    def get_cost_level(row):
        if row["cost_missing"]:
            return "未知"
        cost = row["cost"]
        if cost <= 50:
            return "低价"
        elif cost <= 100:
            return "平价"
        elif cost <= 200:
            return "中端"
        else:
            return "高端"

    df_out["cost_level"] = df_out.apply(get_cost_level, axis=1)

    # ==========2.评分等级 score_level ==========
    def get_score_level(row):
        if row["rating_missing"] or pd.isna(row["rating"]):
            return "未知"
        score = row["rating"]
        if score >= 4.5:
            return "高分优质"
        elif score >= 4.0:
            return "良好"
        elif score >= 3.0:
            return "一般"
        else:
            return "偏低分"

    df_out["score_level"] = df_out.apply(get_score_level, axis=1)

    print("特征工程完成，新增字段 cost_level、score_level")
    print("\n消费等级分布：")
    print(df_out["cost_level"].value_counts())
    print("\n评分等级分布：")
    print(df_out["score_level"].value_counts())

    return df_out


if __name__ == "__main__":
    csv_path = "../data/processed/hangzhou_clean.csv"
    # 编码容错逻辑
    try:
        df_raw = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df_raw = pd.read_csv(csv_path, encoding="gbk")

    df_feature = generate_features(df_raw)
    out_file = "../data/processed/hangzhou_feature.csv"
    df_feature.to_csv(out_file, index=False, encoding="utf-8-sig")
    print(f"\n输出特征完成数据集：{out_file}")
