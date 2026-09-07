import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

# 1. 读取数据
current_dir = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(
    current_dir,
    "..",
    "data",
    "hangzhou_clean.csv"
)

df = pd.read_csv(
    data_path,
    encoding="utf-8"
)

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
# 使用对数降低极低消费餐厅对结果的过度影响
df["性价比"] = (
    df["rating"] /
    np.log1p(df["cost"])
)


# 4. 准备综合评价指标
score_data = df[
    [
        "rating",
        "cost",
        "性价比"
    ]
].copy()


# 5. 指标标准化
scaler = MinMaxScaler()

normalized = scaler.fit_transform(
    score_data
)

normalized_df = pd.DataFrame(
    normalized,
    columns=[
        "评分标准化",
        "消费标准化",
        "性价比标准化"
    ],
    index=df.index
)


# 6. 消费指标反向处理
# 人均消费越低，对消费者越友好
normalized_df["消费友好度"] = (
    1 - normalized_df["消费标准化"]
)


# 7. 设置综合评分权重
rating_weight = 0.45
cost_weight = 0.25
value_weight = 0.30


# 8. 计算综合得分
df["评分标准化"] = (
    normalized_df["评分标准化"]
)

df["消费友好度"] = (
    normalized_df["消费友好度"]
)

df["性价比标准化"] = (
    normalized_df["性价比标准化"]
)

df["综合得分"] = (
    df["评分标准化"] * rating_weight
    + df["消费友好度"] * cost_weight
    + df["性价比标准化"] * value_weight
)


# 9. 将综合得分转换为百分制
df["综合得分"] = (
    df["综合得分"] * 100
).round(2)


# 10. 生成综合排名
df = df.sort_values(
    [
        "综合得分",
        "rating",
        "cost"
    ],
    ascending=[
        False,
        False,
        True
    ]
).reset_index(drop=True)

df["综合排名"] = (
    df.index + 1
)


# 11. 整理综合排行榜
overall_result = df[
    [
        "综合排名",
        "name",
        "adname",
        "type",
        "rating",
        "cost",
        "性价比",
        "评分标准化",
        "消费友好度",
        "性价比标准化",
        "综合得分"
    ]
].copy()


print("\n综合排行榜 Top 30：")
print(
    overall_result
    .head(30)
    .to_string(index=False)
)


# 12. 输出指标权重
print("\n综合得分权重：")
print("评分权重：", rating_weight)
print("消费友好度权重：", cost_weight)
print("性价比权重：", value_weight)


# 13. 保存结果
output_dir = os.path.join(
    current_dir,
    "..",
    "output"
)

os.makedirs(
    output_dir,
    exist_ok=True
)

overall_result.to_csv(
    os.path.join(
        output_dir,
        "overall_ranking.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 14. 保存综合评价指标
indicator_result = df[
    [
        "name",
        "rating",
        "cost",
        "性价比",
        "评分标准化",
        "消费友好度",
        "性价比标准化",
        "综合得分"
    ]
].copy()

indicator_result.to_csv(
    os.path.join(
        output_dir,
        "overall_score_detail.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 15. 输出完成信息
print("\n分析完成！")
print("综合排行榜结果已经保存到 output 文件夹。")