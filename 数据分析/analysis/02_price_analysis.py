import pandas as pd
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


# 2. 处理人均消费

df["cost"] = pd.to_numeric(
    df["cost"],
    errors="coerce"
)

df = df.dropna(subset=["cost"])

print("\n===== 人均消费基本统计 =====")
print(df["cost"].describe())


# 3. 划分消费区间

bins = [0, 50, 100, 150, 200, float("inf")]

labels = [
    "50元以下",
    "50-100元",
    "100-150元",
    "150-200元",
    "200元以上"
]

df["消费区间"] = pd.cut(
    df["cost"],
    bins=bins,
    labels=labels,
    right=False
)


# 4. 各消费区间餐厅数量

price_distribution = (
    df.groupby("消费区间", observed=False)
    .agg(
        餐厅数量=("name", "count"),
        平均评分=("rating", "mean"),
        平均人均消费=("cost", "mean")
    )
    .reset_index()
)

price_distribution["餐厅占比"] = (
    price_distribution["餐厅数量"]
    / len(df)
    * 100
).round(2)

price_distribution["平均评分"] = (
    price_distribution["平均评分"]
    .round(2)
)

price_distribution["平均人均消费"] = (
    price_distribution["平均人均消费"]
    .round(2)
)


print("\n===== 各消费区间分析 =====")
print(
    price_distribution.to_string(index=False)
)


# 5. 各行政区平均消费

district_price = (
    df.groupby("adname")
    .agg(
        餐厅数量=("name", "count"),
        平均人均消费=("cost", "mean"),
        最低人均消费=("cost", "min"),
        最高人均消费=("cost", "max"),
        平均评分=("rating", "mean")
    )
    .reset_index()
)

district_price["平均人均消费"] = (
    district_price["平均人均消费"]
    .round(2)
)

district_price["平均评分"] = (
    district_price["平均评分"]
    .round(2)
)


print("\n===== 各行政区消费水平 =====")

print(
    district_price
    .sort_values(
        "平均人均消费",
        ascending=False
    )
    .to_string(index=False)
)


# 6. 低消费高评分餐厅

# 定义：
# 人均消费 <= 100 元
# 评分 >= 4.5

low_cost_high_rating = df[
    (df["cost"] <= 100) &
    (df["rating"] >= 4.5)
].copy()

low_cost_high_rating = (
    low_cost_high_rating[
        [
            "name",
            "adname",
            "type",
            "rating",
            "cost"
        ]
    ]
    .sort_values(
        ["rating", "cost"],
        ascending=[False, True]
    )
)


print("\n===== 低消费高评分餐厅 Top 20 =====")

print(
    low_cost_high_rating
    .head(20)
    .to_string(index=False)
)


# 7. 保存结果

output_dir = os.path.join(
    current_dir,
    "..",
    "output"
)

os.makedirs(
    output_dir,
    exist_ok=True
)


# 保存消费区间结果
price_distribution.to_csv(
    os.path.join(
        output_dir,
        "price_distribution.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 保存行政区消费结果
district_price.to_csv(
    os.path.join(
        output_dir,
        "district_price_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 保存低消费高评分结果
low_cost_high_rating.to_csv(
    os.path.join(
        output_dir,
        "low_cost_high_rating.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


print("\n===== 分析完成 =====")
print("结果已经保存到 output 文件夹。")