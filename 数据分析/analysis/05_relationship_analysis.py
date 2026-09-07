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


# 2. 处理数据
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
)

print("\n有效数据数量：", len(df))


# 3. 计算评分与人均消费的 Pearson 相关系数
correlation = df["rating"].corr(
    df["cost"],
    method="pearson"
)

print("\n评分与人均消费的 Pearson 相关系数：")
print(round(correlation, 4))


# 4. 判断相关程度
if abs(correlation) < 0.2:
    correlation_level = "相关性很弱"
elif abs(correlation) < 0.4:
    correlation_level = "弱相关"
elif abs(correlation) < 0.6:
    correlation_level = "中等相关"
elif abs(correlation) < 0.8:
    correlation_level = "较强相关"
else:
    correlation_level = "强相关"

if correlation > 0:
    correlation_direction = "正相关"
elif correlation < 0:
    correlation_direction = "负相关"
else:
    correlation_direction = "无明显相关"

print("相关方向：", correlation_direction)
print("相关程度：", correlation_level)


# 5. 按消费区间分析评分
bins = [
    0,
    50,
    100,
    150,
    200,
    float("inf")
]

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

price_rating = (
    df.groupby("消费区间", observed=False)
    .agg(
        餐厅数量=("name", "count"),
        平均评分=("rating", "mean"),
        平均人均消费=("cost", "mean")
    )
    .reset_index()
)

price_rating["平均评分"] = (
    price_rating["平均评分"]
    .round(2)
)

price_rating["平均人均消费"] = (
    price_rating["平均人均消费"]
    .round(2)
)

print("\n各消费区间与评分关系：")
print(
    price_rating.to_string(index=False)
)


# 6. 按行政区分析消费与评分
district_relationship = (
    df.groupby("adname")
    .agg(
        餐厅数量=("name", "count"),
        平均人均消费=("cost", "mean"),
        平均评分=("rating", "mean")
    )
    .reset_index()
)

district_relationship["平均人均消费"] = (
    district_relationship["平均人均消费"]
    .round(2)
)

district_relationship["平均评分"] = (
    district_relationship["平均评分"]
    .round(2)
)

print("\n各行政区消费与评分：")
print(
    district_relationship
    .sort_values("平均评分", ascending=False)
    .to_string(index=False)
)


# 7. 计算行政区层面的消费与评分相关性
district_correlation = (
    district_relationship["平均人均消费"]
    .corr(
        district_relationship["平均评分"],
        method="pearson"
    )
)

print("\n行政区平均消费与平均评分的相关系数：")
print(round(district_correlation, 4))


# 8. 按餐饮类型分析消费与评分
type_relationship = (
    df.groupby("type")
    .agg(
        餐厅数量=("name", "count"),
        平均人均消费=("cost", "mean"),
        平均评分=("rating", "mean")
    )
    .reset_index()
)

# 只保留至少有10家餐厅的类型
type_relationship = type_relationship[
    type_relationship["餐厅数量"] >= 10
].copy()

type_relationship["平均人均消费"] = (
    type_relationship["平均人均消费"]
    .round(2)
)

type_relationship["平均评分"] = (
    type_relationship["平均评分"]
    .round(2)
)

print("\n主要餐饮类型消费与评分：")
print(
    type_relationship
    .sort_values("平均评分", ascending=False)
    .to_string(index=False)
)


# 9. 计算餐饮类型层面的消费与评分相关性
type_correlation = (
    type_relationship["平均人均消费"]
    .corr(
        type_relationship["平均评分"],
        method="pearson"
    )
)

print("\n餐饮类型平均消费与平均评分的相关系数：")
print(round(type_correlation, 4))


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

correlation_result = pd.DataFrame({
    "分析对象": [
        "全部餐厅",
        "行政区",
        "餐饮类型"
    ],
    "相关系数": [
        correlation,
        district_correlation,
        type_correlation
    ]
})

correlation_result["相关系数"] = (
    correlation_result["相关系数"]
    .round(4)
)

correlation_result.to_csv(
    os.path.join(
        output_dir,
        "correlation_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

price_rating.to_csv(
    os.path.join(
        output_dir,
        "price_rating_relationship.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

district_relationship.to_csv(
    os.path.join(
        output_dir,
        "district_relationship.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

type_relationship.to_csv(
    os.path.join(
        output_dir,
        "type_relationship.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 11. 输出完成信息
print("\n分析完成！")
print("关系分析结果已经保存到 output 文件夹。")