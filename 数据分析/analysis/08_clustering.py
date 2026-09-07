import pandas as pd
import numpy as np
import os

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


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
df["性价比"] = (
    df["rating"] /
    np.log1p(df["cost"])
)


# 4. 选择聚类特征
features = [
    "rating",
    "cost",
    "性价比"
]

X = df[features].copy()


# 5. 对聚类特征进行标准化
scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# 6. 测试不同的 K 值
k_results = []

for k in range(2, 7):

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(
        X_scaled
    )

    score = silhouette_score(
        X_scaled,
        labels
    )

    k_results.append({
        "K值": k,
        "轮廓系数": round(score, 4)
    })


k_result_df = pd.DataFrame(
    k_results
)


print("\n不同 K 值的聚类评价：")
print(
    k_result_df.to_string(index=False)
)


# 7. 根据轮廓系数选择最佳 K 值
best_k = int(
    k_result_df.loc[
        k_result_df["轮廓系数"].idxmax(),
        "K值"
    ]
)

best_score = float(
    k_result_df.loc[
        k_result_df["轮廓系数"].idxmax(),
        "轮廓系数"
    ]
)

print("\n最佳 K 值：", best_k)
print("最佳轮廓系数：", best_score)


# 8. 使用最佳 K 值进行最终聚类
final_model = KMeans(
    n_clusters=best_k,
    random_state=42,
    n_init=10
)

df["cluster"] = final_model.fit_predict(
    X_scaled
)


# 9. 统计各聚类的基本特征
cluster_profile = (
    df.groupby("cluster")
    .agg(
        餐厅数量=("name", "count"),
        平均评分=("rating", "mean"),
        平均人均消费=("cost", "mean"),
        平均性价比=("性价比", "mean")
    )
    .reset_index()
)


# 10. 计算各聚类的餐厅占比
cluster_profile["餐厅占比"] = (
    cluster_profile["餐厅数量"]
    / len(df)
    * 100
)

cluster_profile["平均评分"] = (
    cluster_profile["平均评分"]
    .round(2)
)

cluster_profile["平均人均消费"] = (
    cluster_profile["平均人均消费"]
    .round(2)
)

cluster_profile["平均性价比"] = (
    cluster_profile["平均性价比"]
    .round(4)
)

cluster_profile["餐厅占比"] = (
    cluster_profile["餐厅占比"]
    .round(2)
)


# 11. 根据平均人均消费自动确定餐厅类型
cluster_profile = cluster_profile.sort_values(
    "平均人均消费"
).reset_index(drop=True)

if len(cluster_profile) == 3:

    type_names = [
        "平价高性价比型",
        "大众品质型",
        "高消费高品质型"
    ]

    cluster_type_map = dict(
        zip(
            cluster_profile["cluster"],
            type_names
        )
    )

else:

    cluster_type_map = {}

    for i, cluster_id in enumerate(
        cluster_profile["cluster"]
    ):

        if i == 0:
            cluster_type_map[cluster_id] = "低消费型"

        elif i == len(cluster_profile) - 1:
            cluster_type_map[cluster_id] = "高消费型"

        else:
            cluster_type_map[cluster_id] = "大众消费型"


# 12. 给聚类画像添加消费者类型
cluster_profile["餐厅类型"] = (
    cluster_profile["cluster"]
    .map(cluster_type_map)
)


# 13. 给每一家餐厅添加消费者类型
df["餐厅类型"] = (
    df["cluster"]
    .map(cluster_type_map)
)


# 14. 调整聚类画像的列顺序
cluster_profile = cluster_profile[
    [
        "cluster",
        "餐厅类型",
        "餐厅数量",
        "平均评分",
        "平均人均消费",
        "平均性价比",
        "餐厅占比"
    ]
]


# 15. 输出聚类特征
print("\n各聚类特征：")
print(
    cluster_profile.to_string(index=False)
)


# 16. 输出聚类之间的特征差异
print("\n各聚类的特征差异：")

for _, row in cluster_profile.iterrows():

    print(
        row["餐厅类型"],
        "：",
        "餐厅数量 =", int(row["餐厅数量"]),
        "，平均评分 =", row["平均评分"],
        "，平均人均消费 =", row["平均人均消费"],
        "，平均性价比 =", row["平均性价比"],
        "，餐厅占比 =", row["餐厅占比"], "%"
    )


# 17. 查看每个聚类中的代表性餐厅
print("\n各聚类代表性餐厅：")

for cluster_id in sorted(df["cluster"].unique()):

    cluster_data = df[
        df["cluster"] == cluster_id
    ].copy()

    cluster_data = cluster_data.sort_values(
        "rating",
        ascending=False
    )

    cluster_name = cluster_type_map.get(
        cluster_id,
        "未命名类型"
    )

    print(
        "\n",
        cluster_name,
        "Top 5："
    )

    print(
        cluster_data[
            [
                "name",
                "adname",
                "type",
                "rating",
                "cost",
                "性价比"
            ]
        ]
        .head(5)
        .to_string(index=False)
    )


# 18. 创建输出文件夹
output_dir = os.path.join(
    current_dir,
    "..",
    "output"
)

os.makedirs(
    output_dir,
    exist_ok=True
)


# 19. 保存 K 值评价结果
k_result_df.to_csv(
    os.path.join(
        output_dir,
        "clustering_k_evaluation.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 20. 保存聚类特征画像
cluster_profile.to_csv(
    os.path.join(
        output_dir,
        "cluster_profile.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 21. 保存每家餐厅的聚类结果
cluster_result = df[
    [
        "name",
        "adname",
        "type",
        "rating",
        "cost",
        "性价比",
        "cluster",
        "餐厅类型"
    ]
].copy()


cluster_result.to_csv(
    os.path.join(
        output_dir,
        "clustering_result.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 22. 输出完成信息
print("\n分析完成！")
print("K-Means 聚类结果已经保存到 output 文件夹。")