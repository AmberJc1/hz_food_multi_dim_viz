import pandas as pd
import numpy as np
import os

# 1. 读取数据
current_dir = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(
    current_dir,
    "..",
    "data",
    "hangzhou_clean.csv"
)

df = pd.read_csv(data_path, encoding="utf-8")

print("数据读取成功！")
print("数据规模：", df.shape)


# 2. 处理评分和人均消费
df["rating"] = pd.to_numeric(
    df["rating"],
    errors="coerce"
)

df["cost"] = pd.to_numeric(
    df["cost"],
    errors="coerce"
)

df = df.dropna(
    subset=["rating", "cost"]
).copy()


# 3. 计算性价比
# 使用评分除以消费的对数，减少极低消费餐厅对结果的过度影响
df["性价比"] = (
    df["rating"] /
    np.log1p(df["cost"])
)

df["性价比"] = df["性价比"].round(4)


# 4. 高评分排行榜
high_rating = (
    df[
        [
            "name",
            "adname",
            "type",
            "rating",
            "cost",
            "性价比"
        ]
    ]
    .sort_values(
        ["rating", "cost"],
        ascending=[False, True]
    )
    .reset_index(drop=True)
)

high_rating["排名"] = high_rating.index + 1

high_rating = high_rating[
    [
        "排名",
        "name",
        "adname",
        "type",
        "rating",
        "cost",
        "性价比"
    ]
]

print("\n===== 高评分排行榜 Top 20 =====")
print(
    high_rating
    .head(20)
    .to_string(index=False)
)


# 5. 低消费排行榜
low_cost = (
    df[
        [
            "name",
            "adname",
            "type",
            "rating",
            "cost",
            "性价比"
        ]
    ]
    .sort_values(
        ["cost", "rating"],
        ascending=[True, False]
    )
    .reset_index(drop=True)
)

low_cost["排名"] = low_cost.index + 1

low_cost = low_cost[
    [
        "排名",
        "name",
        "adname",
        "type",
        "rating",
        "cost",
        "性价比"
    ]
]

print("\n===== 低消费排行榜 Top 20 =====")
print(
    low_cost
    .head(20)
    .to_string(index=False)
)


# 6. 高性价比排行榜
high_value = (
    df[
        [
            "name",
            "adname",
            "type",
            "rating",
            "cost",
            "性价比"
        ]
    ]
    .sort_values(
        ["性价比", "rating"],
        ascending=[False, False]
    )
    .reset_index(drop=True)
)

high_value["排名"] = high_value.index + 1

high_value = high_value[
    [
        "排名",
        "name",
        "adname",
        "type",
        "rating",
        "cost",
        "性价比"
    ]
]

print("\n===== 高性价比排行榜 Top 20 =====")
print(
    high_value
    .head(20)
    .to_string(index=False)
)


# 7. 低消费高评分排行榜
# 人均消费不超过100元
# 评分不低于4.5
low_cost_high_rating = (
    df[
        (df["cost"] <= 100) &
        (df["rating"] >= 4.5)
    ]
    [
        [
            "name",
            "adname",
            "type",
            "rating",
            "cost",
            "性价比"
        ]
    ]
    .sort_values(
        ["rating", "cost"],
        ascending=[False, True]
    )
    .reset_index(drop=True)
)

low_cost_high_rating["排名"] = (
    low_cost_high_rating.index + 1
)

low_cost_high_rating = low_cost_high_rating[
    [
        "排名",
        "name",
        "adname",
        "type",
        "rating",
        "cost",
        "性价比"
    ]
]

print("\n===== 低消费高评分排行榜 Top 20 =====")
print(
    low_cost_high_rating
    .head(20)
    .to_string(index=False)
)


# 8. 各行政区高评分排行榜
district_ranking = (
    df[
        df["rating"] >= 4.5
    ]
    [
        [
            "name",
            "adname",
            "type",
            "rating",
            "cost",
            "性价比"
        ]
    ]
    .sort_values(
        ["adname", "rating", "cost"],
        ascending=[True, False, True]
    )
    .copy()
)

district_ranking["区内排名"] = (
    district_ranking
    .groupby("adname")
    .cumcount() + 1
)

district_ranking = district_ranking[
    district_ranking["区内排名"] <= 10
]

district_ranking = district_ranking[
    [
        "adname",
        "区内排名",
        "name",
        "type",
        "rating",
        "cost",
        "性价比"
    ]
]

print("\n===== 各行政区高评分餐厅 Top 10 =====")
print(
    district_ranking
    .head(30)
    .to_string(index=False)
)


# 9. 各餐饮类型高评分排行榜
type_ranking = (
    df[
        df["rating"] >= 4.5
    ]
    [
        [
            "name",
            "type",
            "adname",
            "rating",
            "cost",
            "性价比"
        ]
    ]
    .sort_values(
        ["type", "rating", "cost"],
        ascending=[True, False, True]
    )
    .copy()
)

type_ranking["类型内排名"] = (
    type_ranking
    .groupby("type")
    .cumcount() + 1
)

type_ranking = type_ranking[
    type_ranking["类型内排名"] <= 10
]

type_ranking = type_ranking[
    [
        "type",
        "类型内排名",
        "name",
        "adname",
        "rating",
        "cost",
        "性价比"
    ]
]

print("\n===== 各餐饮类型高评分餐厅 Top 10 =====")
print(
    type_ranking
    .head(30)
    .to_string(index=False)
)


# 10. 保存结果
output_dir = os.path.join(
    current_dir,
    "..",
    "output"
)

os.makedirs(
    output_dir,
    exist_ok=True
)

high_rating.to_csv(
    os.path.join(
        output_dir,
        "ranking_high_rating.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

low_cost.to_csv(
    os.path.join(
        output_dir,
        "ranking_low_cost.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

high_value.to_csv(
    os.path.join(
        output_dir,
        "ranking_high_value.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

low_cost_high_rating.to_csv(
    os.path.join(
        output_dir,
        "ranking_low_cost_high_rating.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

district_ranking.to_csv(
    os.path.join(
        output_dir,
        "ranking_by_district.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

type_ranking.to_csv(
    os.path.join(
        output_dir,
        "ranking_by_type.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 11. 输出完成信息
print("\n分析完成！")
print("排行榜结果已经保存到 output 文件夹。")