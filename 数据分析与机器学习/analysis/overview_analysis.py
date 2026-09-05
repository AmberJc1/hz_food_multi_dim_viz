from pathlib import Path
import pandas as pd


# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parents[2]

# 清洗后的特征数据
DATA_PATH = (
    BASE_DIR
    / "数据清洗"
    / "data"
    / "processed"
    / "hangzhou_feature.csv"
)

# 读取 CSV
df = pd.read_csv(DATA_PATH)


print("=" * 60)
print("杭州餐饮商家数据分析")
print("=" * 60)

print("数据读取成功！")
print("数据规模：", df.shape)

print("\n【字段信息】")

for i, col in enumerate(df.columns, start=1):
    print(f"{i}. {col}")

# =========================
# 数据质量检查
# =========================

print("\n【数据质量检查】")

print("\n数据类型：")
print(df.dtypes)

print("\n缺失值统计：")

missing = df.isnull().sum()

missing_rate = (
    df.isnull().mean() * 100
)

missing_table = pd.DataFrame({
    "缺失数量": missing,
    "缺失率": missing_rate.round(2)
})

print(
    missing_table[
        missing_table["缺失数量"] > 0
    ].sort_values(
        "缺失数量",
        ascending=False
    )
)

# =========================
# 核心指标统计
# =========================

print("\n【核心指标统计】")

core_columns = [
    "rating",
    "cost",
    "favorite_num"
]

print(
    df[core_columns].describe()
)

# =========================
# 评分和消费有效数据
# =========================

print("\n【评分和消费数据情况】")

print(
    "评分非空数量：",
    df["rating"].notna().sum()
)

print(
    "消费非空数量：",
    df["cost"].notna().sum()
)

valid_df = df[
    df["rating"].notna()
    & df["cost"].notna()
].copy()

print(
    "评分和消费同时存在：",
    len(valid_df)
)

# =========================
# 评分与消费相关性
# =========================

print("\n【评分与人均消费相关性】")

correlation = valid_df[
    ["rating", "cost"]
].corr()

print(correlation)

corr_value = correlation.loc[
    "rating",
    "cost"
]

print(
    "Pearson相关系数：",
    round(corr_value, 4)
)

# =========================
# 评分与人均消费散点图 + 趋势线
# =========================

import matplotlib.pyplot as plt
import numpy as np


plt.figure(figsize=(10, 6))


# 1. 绘制散点
plt.scatter(
    valid_df["cost"],
    valid_df["rating"],
    alpha=0.6
)


# 2. 计算线性趋势线
x = valid_df["cost"].values
y = valid_df["rating"].values

slope, intercept = np.polyfit(x, y, 1)

x_line = np.linspace(
    x.min(),
    x.max(),
    100
)

y_line = (
    slope * x_line
    + intercept
)


# 3. 绘制趋势线
plt.plot(
    x_line,
    y_line,
    linewidth=2
)


# 4. 设置坐标轴
plt.xlabel("Average Cost")
plt.ylabel("Rating")

plt.title(
    "Relationship between Rating and Average Cost"
)

plt.grid(
    alpha=0.3
)


# 5. 显示相关系数
plt.text(
    0.05,
    0.05,
    f"Pearson r = {corr_value:.4f}",
    transform=plt.gca().transAxes,
    fontsize=12
)


plt.tight_layout()

plt.show()

# =========================
# 查看关键字段的数据
# =========================

print("\n【关键字段示例】")

check_columns = [
    "name",
    "rating",
    "cost",
    "favorite_num",
    "type_main",
    "cat_level1",
    "cat_level2",
    "tag_list"
]

print(
    df[check_columns].head(20).to_string(index=False)
)

# =========================
# 核心指标分布检查
# =========================

print("\n【核心指标有效数据情况】")

core_columns = [
    "rating",
    "cost",
    "favorite_num"
]

for col in core_columns:
    print(
        f"{col}：有效数量={df[col].notna().sum()}，"
        f"缺失数量={df[col].isna().sum()}"
    )


print("\n【核心指标统计】")

print(
    df[core_columns].describe().round(2)
)

# =========================
# 检查收藏数数据类型
# =========================

print("\n【收藏数数据类型】")

print("favorite_num 类型：")
print(df["favorite_num"].dtype)

print("\n收藏数前20条：")
print(df["favorite_num"].head(20).to_string(index=False))

print("\n收藏数统计：")
print(df["favorite_num"].value_counts().head(20))

# =========================
# 检查所有字段的数据类型
# =========================

print("\n【所有字段数据类型】")

print(df.dtypes.to_string())


# =========================
# 检查数值型字段
# =========================

print("\n【数值型字段】")

numeric_columns = df.select_dtypes(
    include=["number"]
).columns.tolist()

print(numeric_columns)


# =========================
# 数值型字段统计
# =========================

print("\n【数值型字段统计】")

print(
    df[numeric_columns]
    .describe()
    .round(2)
)

# =========================
# 检查可能包含数值信息的字符串字段
# =========================

check_columns = [
    "distance",
    "importance",
    "photos",
    "shopinfo"
]

print("\n【可能的数值字段检查】")

for col in check_columns:
    print(f"\n--- {col} ---")
    print("数据类型：", df[col].dtype)
    print("前20条：")
    print(df[col].head(20).tolist())
    print("不同值数量：", df[col].nunique())

# =========================
# 检查 shopinfo 的具体取值
# =========================

print("\n【shopinfo 取值统计】")

print(df["shopinfo"].value_counts().sort_index())

print("\n【shopinfo 与评分、消费的关系】")

print(
    df.groupby("shopinfo")[["rating", "cost"]]
    .agg(["count", "mean"])
    .round(2)
)