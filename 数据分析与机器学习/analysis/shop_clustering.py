import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import matplotlib.pyplot as plt


# =========================
# 1. 读取数据
# =========================

file_path = "数据清洗/data/processed/hangzhou_feature.csv"

df = pd.read_csv(file_path)

print("=" * 60)
print("杭州餐饮商家 K-Means 聚类分析")
print("=" * 60)

print("\n原始数据规模：", df.shape)


# =========================
# 2. 选择聚类特征
# =========================

features = ["rating", "cost"]

cluster_df = df[features].dropna().copy()

print("\n用于聚类的数据量：", len(cluster_df))

print("\n聚类特征：")
print(features)


# =========================
# 3. 数据标准化
# =========================

scaler = StandardScaler()

X = scaler.fit_transform(cluster_df[features])

print("\n数据标准化完成")


# =========================
# 4. 比较不同 K 值
# =========================

print("\n【不同聚类数量的轮廓系数】")

scores = {}

for k in range(2, 6):

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(X)

    score = silhouette_score(X, labels)

    scores[k] = score

    print(f"K={k}，轮廓系数={score:.4f}")


# =========================
# 5. 选择最优 K
# =========================

best_k = max(scores, key=scores.get)

print("\n最优聚类数量：", best_k)

print(
    f"最优轮廓系数：{scores[best_k]:.4f}"
)


# =========================
# 6. 使用最优 K 进行聚类
# =========================

kmeans = KMeans(
    n_clusters=best_k,
    random_state=42,
    n_init=10
)

cluster_df["cluster"] = kmeans.fit_predict(X)


# =========================
# 7. 输出每一类的商家数量
# =========================

print("\n【各聚类商家数量】")

print(
    cluster_df["cluster"]
    .value_counts()
    .sort_index()
)


# =========================
# 8. 输出每一类的特征均值
# =========================

print("\n【各聚类特征均值】")

cluster_summary = (
    cluster_df
    .groupby("cluster")[features]
    .mean()
    .round(2)
)

print(cluster_summary)


# =========================
# 9. 可视化聚类结果
# =========================

plt.figure(figsize=(10, 7))

for cluster_id in sorted(cluster_df["cluster"].unique()):

    data = cluster_df[
        cluster_df["cluster"] == cluster_id
    ]

    plt.scatter(
        data["cost"],
        data["rating"],
        label=f"Cluster {cluster_id}",
        alpha=0.7
    )


plt.xlabel("Average Cost")
plt.ylabel("Rating")

plt.title("杭州餐饮商家 K-Means 聚类结果")

plt.legend()

plt.grid(alpha=0.3)

plt.tight_layout()

plt.show()


# =========================
# 10. 保存聚类结果
# =========================

# 把聚类标签写回原始数据
df.loc[cluster_df.index, "cluster"] = cluster_df["cluster"]

# 保存到“数据分析与机器学习”目录
output_path = "数据分析与机器学习/shop_cluster_result.csv"

df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("\n聚类结果已经保存：")
print(output_path)

print("\n最终数据规模：", df.shape)

# ==============================
# 11. 分析各聚类的餐饮类型
# ==============================

print("\n" + "=" * 60)
print("各聚类的主要餐饮类型")
print("=" * 60)

# 只分析成功参与聚类的商家
cluster_data = df.loc[cluster_df.index].copy()

# 查看每个聚类的主要二级分类
for cluster_id in sorted(cluster_data["cluster"].dropna().unique()):

    data = cluster_data[
        cluster_data["cluster"] == cluster_id
    ]

    print(f"\n【Cluster {int(cluster_id)}】")

    print("商家数量：", len(data))

    print("\n主要餐饮分类：")

    print(
        data["cat_level2"]
        .value_counts()
        .head(5)
    )

    print("\n主要餐饮类型：")

    print(
        data["type_main"]
        .value_counts()
        .head(5)
    )

# ==============================
# 12. 生成聚类画像
# ==============================

print("\n" + "=" * 60)
print("生成聚类画像")
print("=" * 60)

# 聚类名称
cluster_names = {
    0: "高评分大众型",
    1: "低消费基础型",
    2: "大众均衡型",
    3: "高端高消费型",
    4: "中高端品质型"
}

profile_list = []

for cluster_id in sorted(cluster_data["cluster"].dropna().unique()):

    cluster_id = int(cluster_id)

    data = cluster_data[
        cluster_data["cluster"] == cluster_id
    ].copy()

    # 主要餐饮分类
    category_counts = (
        data["cat_level2"]
        .value_counts()
        .head(3)
    )

    # 主要餐饮类型
    type_counts = (
        data["type_main"]
        .value_counts()
        .head(3)
    )

    # 拼接主要分类
    main_categories = "、".join(
        category_counts.index.astype(str)
    )

    # 拼接主要类型
    main_types = "、".join(
        type_counts.index.astype(str)
    )

    profile_list.append({
        "cluster": cluster_id,
        "cluster_name": cluster_names[cluster_id],
        "shop_count": len(data),
        "avg_rating": round(data["rating"].mean(), 2),
        "median_rating": round(data["rating"].median(), 2),
        "avg_cost": round(data["cost"].mean(), 2),
        "median_cost": round(data["cost"].median(), 2),
        "min_cost": round(data["cost"].min(), 2),
        "max_cost": round(data["cost"].max(), 2),
        "main_categories": main_categories,
        "main_types": main_types
    })


# 转换成 DataFrame
profile_df = pd.DataFrame(profile_list)

print("\n【聚类画像】")
print(profile_df.to_string(index=False))


# ==============================
# 保存聚类画像
# ==============================

profile_output = "数据分析与机器学习/cluster_profile.csv"

profile_df.to_csv(
    profile_output,
    index=False,
    encoding="utf-8-sig"
)

print("\n聚类画像已经保存：")
print(profile_output)

print("\n分析完成！")

# ==============================
# 13. 检查可用于机器学习的字段
# ==============================

print("\n" + "=" * 60)
print("机器学习候选特征检查")
print("=" * 60)

# 查看每个字段的数据类型和有效数据数量
feature_check = pd.DataFrame({
    "字段": df.columns,
    "数据类型": df.dtypes.astype(str).values,
    "有效数量": df.notna().sum().values,
    "缺失数量": df.isna().sum().values,
    "唯一值数量": df.nunique().values
})

print("\n【字段有效性检查】")

print(
    feature_check.to_string(index=False)
)

# 保存特征检查结果
feature_output = "数据分析与机器学习/feature_check.csv"

feature_check.to_csv(
    feature_output,
    index=False,
    encoding="utf-8-sig"
)

print("\n特征检查结果已经保存：")
print(feature_output)