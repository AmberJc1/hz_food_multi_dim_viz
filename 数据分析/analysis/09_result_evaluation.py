import pandas as pd
import numpy as np
import os

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans


# 1. 设置文件路径
current_dir = os.path.dirname(os.path.abspath(__file__))

data_path = os.path.join(
    current_dir,
    "..",
    "data",
    "hangzhou_clean.csv"
)

overall_path = os.path.join(
    current_dir,
    "..",
    "output",
    "overall_ranking.csv"
)

relationship_path = os.path.join(
    current_dir,
    "..",
    "output",
    "correlation_result.csv"
)

cluster_path = os.path.join(
    current_dir,
    "..",
    "output",
    "clustering_result.csv"
)


# 2. 读取数据
df = pd.read_csv(
    data_path,
    encoding="utf-8"
)

print("数据读取成功！")
print("原始数据规模：", df.shape)


# 3. 数据质量检查
print("\n数据质量检查：")

missing_result = pd.DataFrame({
    "字段": df.columns,
    "缺失数量": df.isnull().sum().values
})

missing_result["缺失率"] = (
    missing_result["缺失数量"]
    / len(df)
    * 100
)

missing_result["缺失率"] = (
    missing_result["缺失率"]
    .round(2)
)

print("\n各字段缺失情况：")
print(
    missing_result.to_string(index=False)
)


# 4. 检查重复数据
duplicate_count = df.duplicated().sum()

print("\n重复数据数量：", duplicate_count)


# 5. 检查评分和消费数据
df["rating"] = pd.to_numeric(
    df["rating"],
    errors="coerce"
)

df["cost"] = pd.to_numeric(
    df["cost"],
    errors="coerce"
)

rating_invalid = (
    (df["rating"] < 0)
    | (df["rating"] > 5)
).sum()

cost_invalid = (
    df["cost"] < 0
).sum()

print("异常评分数量：", rating_invalid)
print("异常消费数量：", cost_invalid)


# 6. 数据质量总结
quality_summary = pd.DataFrame({
    "检查项目": [
        "原始数据量",
        "重复数据量",
        "评分缺失量",
        "消费缺失量",
        "异常评分量",
        "异常消费量"
    ],
    "结果": [
        len(df),
        duplicate_count,
        df["rating"].isnull().sum(),
        df["cost"].isnull().sum(),
        rating_invalid,
        cost_invalid
    ]
})

print("\n数据质量评价：")
print(
    quality_summary.to_string(index=False)
)


# 7. 计算性价比
evaluation_df = df.dropna(
    subset=["rating", "cost"]
).copy()

evaluation_df = evaluation_df[
    evaluation_df["rating"].between(0, 5)
    & (evaluation_df["cost"] >= 0)
].copy()

evaluation_df["性价比"] = (
    evaluation_df["rating"]
    / np.log1p(evaluation_df["cost"])
)


# 8. 准备综合得分评价指标
score_data = evaluation_df[
    [
        "rating",
        "cost",
        "性价比"
    ]
].copy()


# 9. 指标标准化
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
    index=evaluation_df.index
)

normalized_df["消费友好度"] = (
    1 - normalized_df["消费标准化"]
)


# 10. 定义综合得分计算函数
def calculate_overall_score(
    rating_weight,
    cost_weight,
    value_weight
):
    score = (
        normalized_df["评分标准化"]
        * rating_weight
        + normalized_df["消费友好度"]
        * cost_weight
        + normalized_df["性价比标准化"]
        * value_weight
    )

    return score * 100


# 11. 设置不同权重方案
weight_scenarios = {
    "方案A_基础方案": (0.45, 0.25, 0.30),
    "方案B_提高评分权重": (0.50, 0.20, 0.30),
    "方案C_提高消费权重": (0.40, 0.30, 0.30),
    "方案D_提高性价比权重": (0.45, 0.20, 0.35),
    "方案E_平均权重": (1/3, 1/3, 1/3)
}


# 12. 计算不同权重方案的综合得分
ranking_results = {}

for scenario_name, weights in weight_scenarios.items():

    rating_weight = weights[0]
    cost_weight = weights[1]
    value_weight = weights[2]

    evaluation_df[scenario_name + "_综合得分"] = (
        calculate_overall_score(
            rating_weight,
            cost_weight,
            value_weight
        )
        .round(2)
    )

    ranking_results[scenario_name] = (
        evaluation_df[
            [
                "name",
                scenario_name + "_综合得分"
            ]
        ]
        .sort_values(
            scenario_name + "_综合得分",
            ascending=False
        )
        .reset_index(drop=True)
    )


# 13. 查看不同权重方案的 Top 10
print("\n不同权重方案 Top 10：")

top_n = 10

for scenario_name in weight_scenarios:

    print("\n" + scenario_name)

    print(
        ranking_results[scenario_name]
        .head(top_n)
        .to_string(index=False)
    )


# 14. 计算 Top 10 重合数量
base_top10 = set(
    ranking_results["方案A_基础方案"]
    .head(10)["name"]
)

stability_results = []

for scenario_name in weight_scenarios:

    current_top10 = set(
        ranking_results[scenario_name]
        .head(10)["name"]
    )

    overlap_count = len(
        base_top10
        & current_top10
    )

    overlap_rate = (
        overlap_count / 10 * 100
    )

    stability_results.append({
        "权重方案": scenario_name,
        "Top10重合数量": overlap_count,
        "Top10重合率": round(
            overlap_rate,
            2
        )
    })


stability_df = pd.DataFrame(
    stability_results
)


# 15. 输出排名稳定性
print("\n综合排行榜稳定性评价：")
print(
    stability_df.to_string(index=False)
)


# 16. 计算 Top 20 稳定性
base_top20 = set(
    ranking_results["方案A_基础方案"]
    .head(20)["name"]
)

top20_results = []

for scenario_name in weight_scenarios:

    current_top20 = set(
        ranking_results[scenario_name]
        .head(20)["name"]
    )

    overlap_count = len(
        base_top20
        & current_top20
    )

    overlap_rate = (
        overlap_count / 20 * 100
    )

    top20_results.append({
        "权重方案": scenario_name,
        "Top20重合数量": overlap_count,
        "Top20重合率": round(
            overlap_rate,
            2
        )
    })


top20_df = pd.DataFrame(
    top20_results
)


print("\nTop 20 稳定性评价：")
print(
    top20_df.to_string(index=False)
)


# 17. 读取关系分析结果
if os.path.exists(relationship_path):

    relationship_df = pd.read_csv(
        relationship_path,
        encoding="utf-8-sig"
    )

    print("\n关系分析结果：")
    print(
        relationship_df.to_string(index=False)
    )

else:

    relationship_df = pd.DataFrame()

    print(
        "\n未找到 relationship_result.csv，"
        "跳过关系分析结果读取。"
    )


# 18. 读取聚类结果
if os.path.exists(cluster_path):

    cluster_df = pd.read_csv(
        cluster_path,
        encoding="utf-8-sig"
    )

    print("\n聚类结果读取成功！")
    print(
        "聚类餐厅数量：",
        len(cluster_df)
    )

else:

    cluster_df = pd.DataFrame()

    print(
        "\n未找到 clustering_result.csv，"
        "跳过聚类结果读取。"
    )


# 19. 重新评价不同 K 值
print("\nK-Means 聚类稳定性评价：")

cluster_features = evaluation_df[
    [
        "rating",
        "cost",
        "性价比"
    ]
].copy()

cluster_scaler = StandardScaler()

cluster_X = cluster_scaler.fit_transform(
    cluster_features
)

cluster_k_results = []

for k in range(2, 7):

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(
        cluster_X
    )

    score = silhouette_score(
        cluster_X,
        labels
    )

    cluster_k_results.append({
        "K值": k,
        "轮廓系数": round(score, 4)
    })


cluster_k_df = pd.DataFrame(
    cluster_k_results
)

print(
    cluster_k_df.to_string(index=False)
)


# 20. 获取最佳聚类 K 值
best_k_row = cluster_k_df.loc[
    cluster_k_df["轮廓系数"].idxmax()
]

best_k = int(
    best_k_row["K值"]
)

best_silhouette = float(
    best_k_row["轮廓系数"]
)

print("\n最佳 K 值：", best_k)
print("最佳轮廓系数：", best_silhouette)


# 21. 评价聚类之间的差异
final_cluster_model = KMeans(
    n_clusters=best_k,
    random_state=42,
    n_init=10
)

evaluation_df["cluster"] = (
    final_cluster_model.fit_predict(
        cluster_X
    )
)

cluster_difference = (
    evaluation_df
    .groupby("cluster")
    .agg(
        餐厅数量=("name", "count"),
        平均评分=("rating", "mean"),
        平均人均消费=("cost", "mean"),
        平均性价比=("性价比", "mean")
    )
    .reset_index()
)

cluster_difference["平均评分"] = (
    cluster_difference["平均评分"]
    .round(2)
)

cluster_difference["平均人均消费"] = (
    cluster_difference["平均人均消费"]
    .round(2)
)

cluster_difference["平均性价比"] = (
    cluster_difference["平均性价比"]
    .round(4)
)


print("\n聚类之间的特征差异：")
print(
    cluster_difference.to_string(index=False)
)


# 22. 创建评价结果文件夹
output_dir = os.path.join(
    current_dir,
    "..",
    "output"
)

os.makedirs(
    output_dir,
    exist_ok=True
)


# 23. 保存数据质量检查结果
quality_summary.to_csv(
    os.path.join(
        output_dir,
        "evaluation_data_quality.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 24. 保存综合排行榜稳定性结果
stability_df.to_csv(
    os.path.join(
        output_dir,
        "ranking_stability_top10.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)

top20_df.to_csv(
    os.path.join(
        output_dir,
        "ranking_stability_top20.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 25. 保存 K 值评价结果
cluster_k_df.to_csv(
    os.path.join(
        output_dir,
        "evaluation_clustering_k.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 26. 保存聚类差异结果
cluster_difference.to_csv(
    os.path.join(
        output_dir,
        "evaluation_cluster_difference.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 27. 保存综合评价总结
summary = pd.DataFrame({
    "评价项目": [
        "原始数据量",
        "重复数据量",
        "异常评分数量",
        "异常消费数量",
        "综合排行榜基础权重",
        "Top10基础方案稳定性",
        "Top20基础方案稳定性",
        "最佳聚类K值",
        "最佳轮廓系数"
    ],
    "评价结果": [
        len(df),
        duplicate_count,
        rating_invalid,
        cost_invalid,
        "评分45% + 消费友好度25% + 性价比30%",
        str(
            stability_df.iloc[1:]["Top10重合率"].tolist()
        ),
        str(
            top20_df.iloc[1:]["Top20重合率"].tolist()
        ),
        best_k,
        best_silhouette
    ]
})


summary.to_csv(
    os.path.join(
        output_dir,
        "final_evaluation_summary.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)


# 28. 输出完成信息
print("\n分析完成！")
print("最终结果评价已经保存到 output 文件夹。")