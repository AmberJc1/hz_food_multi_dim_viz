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
)


# 3. 分析主要餐饮类型
# type 字段包含多个层级，用分号分开
type_data = []

for index, row in df.iterrows():
    if pd.isna(row["type"]):
        continue

    types = str(row["type"]).split(";")

    # 去掉重复标签
    types = list(dict.fromkeys(types))

    for restaurant_type in types:
        if restaurant_type.strip():
            type_data.append({
                "name": row["name"],
                "type": restaurant_type.strip(),
                "rating": row["rating"],
                "cost": row["cost"]
            })

type_df = pd.DataFrame(type_data)


# 4. 统计各餐饮类型数量
type_result = (
    type_df.groupby("type")
    .agg(
        餐厅数量=("name", "nunique"),
        平均评分=("rating", "mean"),
        平均人均消费=("cost", "mean")
    )
    .reset_index()
)

type_result["平均评分"] = (
    type_result["平均评分"]
    .round(2)
)

type_result["平均人均消费"] = (
    type_result["平均人均消费"]
    .round(2)
)

type_result = type_result.sort_values(
    "餐厅数量",
    ascending=False
)


print("\n===== 各餐饮类型分析 =====")
print(
    type_result.head(20).to_string(index=False)
)


# 5. 筛选主要餐饮类型
# 餐厅数量至少为 10 家，避免样本太少造成误判
main_type_result = type_result[
    type_result["餐厅数量"] >= 10
].copy()


print("\n===== 主要餐饮类型 =====")
print(
    main_type_result.to_string(index=False)
)


# 6. 按平均评分排名
type_rating_result = (
    main_type_result
    .sort_values(
        ["平均评分", "餐厅数量"],
        ascending=[False, False]
    )
    .reset_index(drop=True)
)

type_rating_result["评分排名"] = (
    type_rating_result.index + 1
)


print("\n===== 餐饮类型评分排名 =====")
print(
    type_rating_result[
        [
            "评分排名",
            "type",
            "餐厅数量",
            "平均评分",
            "平均人均消费"
        ]
    ]
    .to_string(index=False)
)


# 7. 按平均人均消费排名
type_cost_result = (
    main_type_result
    .sort_values(
        "平均人均消费",
        ascending=False
    )
    .reset_index(drop=True)
)

type_cost_result["消费排名"] = (
    type_cost_result.index + 1
)


print("\n===== 餐饮类型消费排名 =====")
print(
    type_cost_result[
        [
            "消费排名",
            "type",
            "餐厅数量",
            "平均人均消费",
            "平均评分"
        ]
    ]
    .to_string(index=False)
)


# 8. 分析主要菜系标签
tag_data = []

for index, row in df.iterrows():
    if pd.isna(row["keytag"]):
        continue

    tags = str(row["keytag"]).split(";")

    tags = list(dict.fromkeys(tags))

    for tag in tags:
        if tag.strip():
            tag_data.append({
                "name": row["name"],
                "keytag": tag.strip(),
                "rating": row["rating"],
                "cost": row["cost"]
            })

tag_df = pd.DataFrame(tag_data)


# 9. 菜系标签统计
tag_result = (
    tag_df.groupby("keytag")
    .agg(
        餐厅数量=("name", "nunique"),
        平均评分=("rating", "mean"),
        平均人均消费=("cost", "mean")
    )
    .reset_index()
)

tag_result["平均评分"] = (
    tag_result["平均评分"]
    .round(2)
)

tag_result["平均人均消费"] = (
    tag_result["平均人均消费"]
    .round(2)
)

tag_result = tag_result.sort_values(
    "餐厅数量",
    ascending=False
)


print("\n===== 菜系标签 Top 20 =====")
print(
    tag_result.head(20).to_string(index=False)
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

type_result.to_csv(
    os.path.join(
        output_dir,
        "type_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

type_rating_result.to_csv(
    os.path.join(
        output_dir,
        "type_rating_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

type_cost_result.to_csv(
    os.path.join(
        output_dir,
        "type_cost_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

tag_result.to_csv(
    os.path.join(
        output_dir,
        "tag_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 11. 输出完成信息
print("\n分析完成！")
print("餐饮类型分析结果已经保存到 output 文件夹。")