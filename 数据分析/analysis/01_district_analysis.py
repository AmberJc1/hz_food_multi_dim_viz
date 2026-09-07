import pandas as pd
import os


# 1. 读取数据

current_dir = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(current_dir, "..", "data", "hangzhou_clean.csv")

df = pd.read_csv(data_path, encoding="utf-8")

print("数据读取成功！")
print("数据规模：", df.shape)


# 2. 数据基本检查

print("\n===== 数据基本信息 =====")
print(df[["adname", "rating", "cost"]].info())

print("\n===== 行政区数量 =====")
print(df["adname"].nunique())

print("\n===== 各行政区餐厅数量 =====")
print(df["adname"].value_counts())


# 3. 行政区基础统计

district_result = df.groupby("adname").agg(
    餐厅数量=("name", "count"),
    平均评分=("rating", "mean"),
    平均人均消费=("cost", "mean"),
    最高评分=("rating", "max"),
    最低评分=("rating", "min")
).reset_index()


# 4. 评分最高的行政区

district_result = district_result.sort_values(
    "平均评分",
    ascending=False
)

print("\n===== 各行政区平均评分 =====")
print(district_result.to_string(index=False))


# 5. 人均消费最高的行政区

print("\n===== 各行政区平均人均消费 =====")

print(
    district_result
    .sort_values("平均人均消费", ascending=False)
    [["adname", "平均人均消费"]]
    .to_string(index=False)
)


# 6. 计算高评分餐厅数量

high_rating = (
    df[df["rating"] >= 4.5]
    .groupby("adname")
    .size()
    .reset_index(name="高评分餐厅数量")
)

district_result = district_result.merge(
    high_rating,
    on="adname",
    how="left"
)

district_result["高评分餐厅数量"] = (
    district_result["高评分餐厅数量"]
    .fillna(0)
    .astype(int)
)


# 7. 计算高评分餐厅占比

district_result["高评分餐厅占比"] = (
    district_result["高评分餐厅数量"]
    / district_result["餐厅数量"]
    * 100
).round(2)


# 8. 保存结果

output_dir = os.path.join(current_dir, "..", "output")

os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(
    output_dir,
    "district_result.csv"
)

district_result.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("\n===== 分析完成 =====")
print("结果已经保存到：")
print(output_path)

print("\n===== 最终行政区分析结果 =====")
print(district_result.to_string(index=False))