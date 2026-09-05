import pandas as pd
import os


# ============================================================
# 杭州餐饮商家多维数据分析
# 机器学习结果汇总
# ============================================================

print("=" * 70)
print("杭州餐饮商家机器学习结果汇总")
print("=" * 70)


# ============================================================
# 1. 输出目录
# ============================================================

output_dir = "数据分析与机器学习"


# ============================================================
# 2. 汇总聚类结果
# ============================================================

print("\n【1. K-Means 聚类结果】")

cluster_profile_path = os.path.join(
    output_dir,
    "cluster_profile.csv"
)

if os.path.exists(cluster_profile_path):

    cluster_profile = pd.read_csv(
        cluster_profile_path
    )

    print(cluster_profile.to_string(index=False))

else:

    print("未找到 cluster_profile.csv")


# ============================================================
# 3. 汇总模型比较结果
# ============================================================

print("\n" + "=" * 70)
print("【2. 消费预测模型比较】")
print("=" * 70)

model_comparison_path = os.path.join(
    output_dir,
    "model_comparison.csv"
)

if os.path.exists(model_comparison_path):

    model_comparison = pd.read_csv(
        model_comparison_path
    )

    print(model_comparison.to_string(index=False))

else:

    print("未找到 model_comparison.csv")


# ============================================================
# 4. 汇总最终特征重要性
# ============================================================

print("\n" + "=" * 70)
print("【3. 最终模型 Top 15 特征】")
print("=" * 70)

importance_path = os.path.join(
    output_dir,
    "final_feature_importance.csv"
)

if os.path.exists(importance_path):

    importance = pd.read_csv(
        importance_path
    )

    top15 = importance.head(15)

    print(
        top15.to_string(index=False)
    )

else:

    print("未找到 final_feature_importance.csv")


# ============================================================
# 5. 汇总热门标签
# ============================================================

print("\n" + "=" * 70)
print("【4. Top 20 餐饮标签】")
print("=" * 70)

tag_path = os.path.join(
    output_dir,
    "tag_frequency.csv"
)

if os.path.exists(tag_path):

    tag_frequency = pd.read_csv(
        tag_path
    )

    print(
        tag_frequency.head(20)
        .to_string(index=False)
    )

else:

    print("未找到 tag_frequency.csv")


# ============================================================
# 6. 生成机器学习结论表
# ============================================================

summary = pd.DataFrame({

    "分析模块": [
        "K-Means聚类",
        "评分与消费相关性",
        "消费预测模型",
        "消费预测模型",
        "特征重要性"
    ],

    "核心结果": [
        "最优K=5，轮廓系数=0.5541",
        "Pearson相关系数 r=0.2775",
        "Log Cost：MAE=63.26，RMSE=107.16，R²=0.0133",
        "Log Cost + tag_list：MAE=58.97，RMSE=102.70，R²=0.0626",
        "快餐厅、鹅肝、鲍鱼、外国餐厅、下午茶等特征重要性较高"
    ],

    "分析结论": [
        "218家完整样本可以划分为5类消费画像",
        "评分与消费呈弱正相关",
        "仅使用基础消费特征时预测能力较弱",
        "加入细粒度餐饮标签后模型表现有所改善",
        "餐饮类别、菜品标签和消费场景包含一定消费水平信息"
    ]

})


# ============================================================
# 7. 保存汇总结果
# ============================================================

summary_path = os.path.join(
    output_dir,
    "machine_learning_summary.csv"
)

summary.to_csv(
    summary_path,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. 输出最终汇总
# ============================================================

print("\n" + "=" * 70)
print("【最终机器学习结果汇总】")
print("=" * 70)

print(
    summary.to_string(index=False)
)


print("\n" + "=" * 70)

print("机器学习结果汇总已经保存：")

print(summary_path)

print("\n分析完成！")