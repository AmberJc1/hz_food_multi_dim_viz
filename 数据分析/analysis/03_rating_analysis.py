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


# 2. 处理评分数据
df["rating"] = pd.to_numeric(
    df["rating"],
    errors="coerce"
)

df = df.dropna(subset=["rating"])

print("\n评分数据数量：", len(df))
print("\n评分基本统计：")
print(df["rating"].describe())


# 3. 统计不同评分的餐厅数量
rating_distribution = (
    df["rating"]
    .value_counts()
    .sort_index(ascending=False)
    .reset_index()
)

rating_distribution.columns = [
    "评分",
    "餐厅数量"
]

rating_distribution["餐厅占比"] = (
    rating_distribution["餐厅数量"]
    / len(df)
    * 100
).round(2)

print("\n===== 评分分布 =====")
print(
    rating_distribution.to_string(index=False)
)


# 4. 按评分区间统计
bins = [0, 4.0, 4.3, 4.5, 4.7, 5.0]

labels = [
    "4.0以下",
    "4.0-4.3",
    "4.3-4.5",
    "4.5-4.7",
    "4.7-5.0"
]

df["评分区间"] = pd.cut(
    df["rating"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

rating_interval = (
    df.groupby("评分区间", observed=False)
    .agg(
        餐厅数量=("name", "count"),
        平均人均消费=("cost", "mean")
    )
    .reset_index()
)

rating_interval["餐厅占比"] = (
    rating_interval["餐厅数量"]
    / len(df)
    * 100
).round(2)

rating_interval["平均人均消费"] = (
    rating_interval["平均人均消费"]
    .round(2)
)

print("\n===== 各评分区间分析 =====")
print(
    rating_interval.to_string(index=False)
)


# 5. 各行政区评分分析
district_rating = (
    df.groupby("adname")
    .agg(
        餐厅数量=("name", "count"),
        平均评分=("rating", "mean"),
        最高评分=("rating", "max"),
        最低评分=("rating", "min"),
        评分标准差=("rating", "std")
    )
    .reset_index()
)

district_rating["平均评分"] = (
    district_rating["平均评分"]
    .round(2)
)

district_rating["评分标准差"] = (
    district_rating["评分标准差"]
    .round(2)
)

print("\n===== 各行政区评分分析 =====")
print(
    district_rating
    .sort_values("平均评分", ascending=False)
    .to_string(index=False)
)


# 6. 各餐饮类型评分分析
type_rating = (
    df.groupby("type")
    .agg(
        餐厅数量=("name", "count"),
        平均评分=("rating", "mean"),
        平均人均消费=("cost", "mean")
    )
    .reset_index()
)

type_rating["平均评分"] = (
    type_rating["平均评分"]
    .round(2)
)

type_rating["平均人均消费"] = (
    type_rating["平均人均消费"]
    .round(2)
)

print("\n===== 各餐饮类型评分分析 =====")
print(
    type_rating
    .sort_values(
        ["平均评分", "餐厅数量"],
        ascending=[False, False]
    )
    .to_string(index=False)
)


# 7. 筛选高评分餐厅
high_rating = df[
    df["rating"] >= 4.5
].copy()

high_rating = (
    high_rating[
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

print("\n===== 高评分餐厅数量 =====")
print("评分 >= 4.5 的餐厅数量：", len(high_rating))

print("\n===== 高评分餐厅 Top 20 =====")
print(
    high_rating
    .head(20)
    .to_string(index=False)
)


# 8. 保存结果
output_dir = os.path.join(
    current_dir,
    "..",
    "output"
)

os.makedirs(
    output_dir,
    exist_ok=True
)

rating_distribution.to_csv(
    os.path.join(
        output_dir,
        "rating_distribution.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

rating_interval.to_csv(
    os.path.join(
        output_dir,
        "rating_interval_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

district_rating.to_csv(
    os.path.join(
        output_dir,
        "district_rating_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

type_rating.to_csv(
    os.path.join(
        output_dir,
        "type_rating_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

high_rating.to_csv(
    os.path.join(
        output_dir,
        "high_rating_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 9. 输出完成信息
print("\n分析完成！")
print("评分分析结果已经保存到 output 文件夹。")