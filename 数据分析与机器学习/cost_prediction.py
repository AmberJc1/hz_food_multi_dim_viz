import pandas as pd


# ==============================
# 1. 读取数据
# ==============================

file_path = "数据清洗/data/processed/hangzhou_feature.csv"

df = pd.read_csv(file_path)

print("=" * 60)
print("杭州餐饮商家消费水平机器学习分析")
print("=" * 60)

print("\n原始数据规模：", df.shape)


# ==============================
# 2. 选择机器学习字段
# ==============================

target = "cost"

features = [
    "type_main",
    "cat_level1",
    "cat_level2"
]


print("\n机器学习目标变量：")
print(target)

print("\n机器学习候选特征：")
print(features)


# ==============================
# 3. 筛选有效数据
# ==============================

ml_df = df[
    features + [target]
].dropna().copy()


print("\n用于机器学习的数据量：")
print(len(ml_df))


# ==============================
# 4. 检查数据
# ==============================

print("\n【机器学习数据检查】")

print(
    ml_df[features + [target]]
    .head()
)


print("\n各特征唯一值数量：")

for column in features:

    print(
        f"{column}："
        f"{ml_df[column].nunique()} 类"
    )


# ==============================
# 5. 输出目标变量统计
# ==============================

print("\n【消费水平统计】")

print(
    ml_df[target]
    .describe()
    .round(2)
)


# ==============================
# 6. 保存机器学习数据集
# ==============================

output_path = (
    "数据分析与机器学习/"
    "cost_prediction_dataset.csv"
)

ml_df.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("\n机器学习数据集已经保存：")
print(output_path)

# ==============================
# 7. One-Hot 编码
# ==============================

print("\n" + "=" * 60)
print("开始进行 One-Hot 编码")
print("=" * 60)

# 对分类变量进行独热编码
X = pd.get_dummies(
    ml_df[features],
    columns=features,
    dtype=int
)

# 目标变量
y = ml_df[target]


# ==============================
# 8. 查看编码结果
# ==============================

print("\n原始特征数量：")
print(len(features))

print("\nOne-Hot 编码后的特征数量：")
print(X.shape[1])

print("\n编码后的数据规模：")
print(X.shape)

print("\n编码后的前5行：")
print(X.head())


# ==============================
# 9. 保存编码后的数据
# ==============================

encoded_df = X.copy()

encoded_df["cost"] = y.values

encoded_output = (
    "数据分析与机器学习/"
    "cost_prediction_encoded.csv"
)

encoded_df.to_csv(
    encoded_output,
    index=False,
    encoding="utf-8-sig"
)

print("\n编码后的机器学习数据集已经保存：")
print(encoded_output)

# ==============================
# 10. 划分训练集和测试集
# ==============================

from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

import numpy as np


print("\n" + "=" * 60)
print("开始训练随机森林回归模型")
print("=" * 60)


# ==============================
# 训练集 / 测试集划分
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


print("\n训练集数量：", len(X_train))
print("测试集数量：", len(X_test))


# ==============================
# 创建随机森林模型
# ==============================

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=6,
    min_samples_leaf=3,
    random_state=42
)


# ==============================
# 训练模型
# ==============================

print("\n开始训练模型...")

model.fit(
    X_train,
    y_train
)

print("模型训练完成！")


# ==============================
# 进行预测
# ==============================

y_pred = model.predict(X_test)


# ==============================
# 模型评价
# ==============================

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)

r2 = r2_score(
    y_test,
    y_pred
)


print("\n【模型评价结果】")

print(
    f"MAE  = {mae:.2f}"
)

print(
    f"RMSE = {rmse:.2f}"
)

print(
    f"R²   = {r2:.4f}"
)


# ==============================
# 与简单平均值模型比较
# ==============================

baseline_pred = np.full(
    len(y_test),
    y_train.mean()
)

baseline_mae = mean_absolute_error(
    y_test,
    baseline_pred
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        baseline_pred
    )
)

baseline_r2 = r2_score(
    y_test,
    baseline_pred
)


print("\n【基准模型（直接预测平均消费）】")

print(
    f"MAE  = {baseline_mae:.2f}"
)

print(
    f"RMSE = {baseline_rmse:.2f}"
)

print(
    f"R²   = {baseline_r2:.4f}"
)


# ==============================
# 特征重要性
# ==============================

importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance": model.feature_importances_
})

importance_df = (
    importance_df
    .sort_values(
        "importance",
        ascending=False
    )
)


print("\n【Top 15 特征重要性】")

print(
    importance_df
    .head(15)
    .to_string(index=False)
)


# ==============================
# 保存模型评价结果
# ==============================

model_result = pd.DataFrame({
    "model": [
        "Random Forest",
        "Baseline"
    ],
    "MAE": [
        mae,
        baseline_mae
    ],
    "RMSE": [
        rmse,
        baseline_rmse
    ],
    "R2": [
        r2,
        baseline_r2
    ]
})

model_result.to_csv(
    "数据分析与机器学习/model_evaluation.csv",
    index=False,
    encoding="utf-8-sig"
)


# ==============================
# 保存特征重要性
# ==============================

importance_df.to_csv(
    "数据分析与机器学习/feature_importance.csv",
    index=False,
    encoding="utf-8-sig"
)


print("\n模型评价结果已经保存：")
print("数据分析与机器学习/model_evaluation.csv")

print("\n特征重要性已经保存：")
print("数据分析与机器学习/feature_importance.csv")

# ==============================
# 11. 5折交叉验证
# ==============================

from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score


print("\n" + "=" * 60)
print("开始进行 5 折交叉验证")
print("=" * 60)


# 创建5折交叉验证
kf = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


cv_mae = []
cv_rmse = []
cv_r2 = []


# ==============================
# 进行5折训练
# ==============================

for fold, (train_index, test_index) in enumerate(
    kf.split(X),
    start=1
):

    X_train_cv = X.iloc[train_index]
    X_test_cv = X.iloc[test_index]

    y_train_cv = y.iloc[train_index]
    y_test_cv = y.iloc[test_index]


    # 每一折重新创建模型
    cv_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=6,
        min_samples_leaf=3,
        random_state=42
    )


    # 训练
    cv_model.fit(
        X_train_cv,
        y_train_cv
    )


    # 预测
    y_pred_cv = cv_model.predict(
        X_test_cv
    )


    # 计算指标
    fold_mae = mean_absolute_error(
        y_test_cv,
        y_pred_cv
    )


    fold_rmse = np.sqrt(
        mean_squared_error(
            y_test_cv,
            y_pred_cv
        )
    )


    fold_r2 = r2_score(
        y_test_cv,
        y_pred_cv
    )


    cv_mae.append(fold_mae)
    cv_rmse.append(fold_rmse)
    cv_r2.append(fold_r2)


    print(
        f"\n第 {fold} 折："
    )

    print(
        f"MAE  = {fold_mae:.2f}"
    )

    print(
        f"RMSE = {fold_rmse:.2f}"
    )

    print(
        f"R²   = {fold_r2:.4f}"
    )


# ==============================
# 计算平均结果
# ==============================

print("\n" + "-" * 60)
print("【5折交叉验证平均结果】")
print("-" * 60)


print(
    f"平均 MAE  = "
    f"{np.mean(cv_mae):.2f}"
)


print(
    f"平均 RMSE = "
    f"{np.mean(cv_rmse):.2f}"
)


print(
    f"平均 R²   = "
    f"{np.mean(cv_r2):.4f}"
)


print(
    f"R² 标准差 = "
    f"{np.std(cv_r2):.4f}"
)


print("\n交叉验证完成！")

# ==============================
# 12. Log Cost 随机森林模型
# ==============================

print("\n" + "=" * 60)
print("开始测试 Log Cost 随机森林模型")
print("=" * 60)


# ==============================
# 对消费金额进行对数变换
# ==============================

y_log = np.log1p(y)


print("\n原始消费示例：")
print(y.head().to_list())


print("\nLog(1 + cost) 示例：")
print(y_log.head().round(4).to_list())


# ==============================
# 5折交叉验证
# ==============================

log_mae = []
log_rmse = []
log_r2 = []


for fold, (train_index, test_index) in enumerate(
    kf.split(X),
    start=1
):

    X_train_cv = X.iloc[train_index]
    X_test_cv = X.iloc[test_index]

    y_train_cv = y_log.iloc[train_index]
    y_test_cv = y_log.iloc[test_index]


    # 创建模型
    log_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=6,
        min_samples_leaf=3,
        random_state=42
    )


    # 训练 Log Cost
    log_model.fit(
        X_train_cv,
        y_train_cv
    )


    # 预测 Log Cost
    y_pred_log = log_model.predict(
        X_test_cv
    )


    # 转换回原始消费金额
    y_pred_original = np.expm1(
        y_pred_log
    )

    y_test_original = np.expm1(
        y_test_cv
    )


    # 评价
    fold_mae = mean_absolute_error(
        y_test_original,
        y_pred_original
    )


    fold_rmse = np.sqrt(
        mean_squared_error(
            y_test_original,
            y_pred_original
        )
    )


    fold_r2 = r2_score(
        y_test_original,
        y_pred_original
    )


    log_mae.append(fold_mae)
    log_rmse.append(fold_rmse)
    log_r2.append(fold_r2)


    print(
        f"\n第 {fold} 折："
    )

    print(
        f"MAE  = {fold_mae:.2f}"
    )

    print(
        f"RMSE = {fold_rmse:.2f}"
    )

    print(
        f"R²   = {fold_r2:.4f}"
    )


# ==============================
# 输出平均结果
# ==============================

print("\n" + "-" * 60)

print("【Log Cost 模型 5 折交叉验证平均结果】")

print("-" * 60)


print(
    f"平均 MAE  = "
    f"{np.mean(log_mae):.2f}"
)


print(
    f"平均 RMSE = "
    f"{np.mean(log_rmse):.2f}"
)


print(
    f"平均 R²   = "
    f"{np.mean(log_r2):.4f}"
)


print(
    f"R² 标准差 = "
    f"{np.std(log_r2):.4f}"
)


print("\nLog Cost 模型测试完成！")

# ==============================
# 13. 分析 tag_list 标签
# ==============================

import ast
from collections import Counter


print("\n" + "=" * 60)
print("开始分析 tag_list 标签")
print("=" * 60)


# ==============================
# 只使用有 cost 的 218 家商家
# ==============================

tag_data = df.loc[ml_df.index, "tag_list"].copy()


# ==============================
# 将字符串形式的列表转换成真正的列表
# ==============================

def parse_tags(value):

    try:

        tags = ast.literal_eval(value)

        if isinstance(tags, list):

            return [
                str(tag).strip()
                for tag in tags
                if str(tag).strip()
            ]

        return []

    except:

        return []


parsed_tags = tag_data.apply(
    parse_tags
)


# ==============================
# 统计每个标签出现次数
# ==============================

tag_counter = Counter()

for tags in parsed_tags:

    tag_counter.update(tags)


# 转换成 DataFrame
tag_frequency = pd.DataFrame(
    tag_counter.items(),
    columns=[
        "tag",
        "count"
    ]
)


tag_frequency = (
    tag_frequency
    .sort_values(
        "count",
        ascending=False
    )
    .reset_index(drop=True)
)


# ==============================
# 输出标签统计
# ==============================

print("\n标签总数量：")
print(len(tag_frequency))


print("\n【出现次数最多的 Top 30 标签】")

print(
    tag_frequency
    .head(30)
    .to_string(index=False)
)


# ==============================
# 统计不同出现频率
# ==============================

print("\n【标签出现次数分布】")

print(
    tag_frequency["count"]
    .value_counts()
    .sort_index()
)


# ==============================
# 保存标签频率
# ==============================

tag_output = (
    "数据分析与机器学习/"
    "tag_frequency.csv"
)

tag_frequency.to_csv(
    tag_output,
    index=False,
    encoding="utf-8-sig"
)


print("\n标签频率统计已经保存：")
print(tag_output)


print("\n标签分析完成！")

# ==============================
# 14. 加入高频 tag_list 特征
# ==============================

from sklearn.preprocessing import MultiLabelBinarizer


print("\n" + "=" * 60)
print("开始加入高频 tag_list 特征")
print("=" * 60)


# ==============================
# 选择高频标签
# ==============================

# 保留出现次数 >= 5 的标签
selected_tags = (
    tag_frequency[
        tag_frequency["count"] >= 5
    ]["tag"]
    .tolist()
)


print("\n筛选条件：标签出现次数 >= 5")

print(
    "保留标签数量：",
    len(selected_tags)
)

print("\n保留的标签：")

print(selected_tags)


# ==============================
# 构造标签特征
# ==============================

def filter_tags(tags):

    return [
        tag
        for tag in tags
        if tag in selected_tags
    ]


filtered_tags = parsed_tags.apply(
    filter_tags
)


# ==============================
# Multi-Hot 编码
# ==============================

mlb = MultiLabelBinarizer(
    classes=selected_tags
)


tag_encoded = pd.DataFrame(
    mlb.fit_transform(filtered_tags),
    columns=[
        "tag_" + tag
        for tag in mlb.classes_
    ],
    index=ml_df.index
)


print("\nTag 编码后的特征数量：")

print(
    tag_encoded.shape[1]
)


# ==============================
# 合并原来的分类特征
# ==============================

X_with_tags = pd.concat(
    [
        X,
        tag_encoded
    ],
    axis=1
)


print("\n加入 tag_list 后的总特征数量：")

print(
    X_with_tags.shape[1]
)


print("\n加入 tag_list 后的数据规模：")

print(
    X_with_tags.shape
)


# ==============================
# 5折交叉验证
# ==============================

tag_mae = []
tag_rmse = []
tag_r2 = []


for fold, (train_index, test_index) in enumerate(
    kf.split(X_with_tags),
    start=1
):

    X_train_cv = X_with_tags.iloc[
        train_index
    ]

    X_test_cv = X_with_tags.iloc[
        test_index
    ]

    y_train_cv = y_log.iloc[
        train_index
    ]

    y_test_cv = y_log.iloc[
        test_index
    ]


    # 创建随机森林
    tag_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=6,
        min_samples_leaf=3,
        random_state=42
    )


    # 训练
    tag_model.fit(
        X_train_cv,
        y_train_cv
    )


    # 预测
    y_pred_log = tag_model.predict(
        X_test_cv
    )


    # 转换回原始消费金额
    y_pred_original = np.expm1(
        y_pred_log
    )

    y_test_original = np.expm1(
        y_test_cv
    )


    # 计算指标
    fold_mae = mean_absolute_error(
        y_test_original,
        y_pred_original
    )


    fold_rmse = np.sqrt(
        mean_squared_error(
            y_test_original,
            y_pred_original
        )
    )


    fold_r2 = r2_score(
        y_test_original,
        y_pred_original
    )


    tag_mae.append(
        fold_mae
    )

    tag_rmse.append(
        fold_rmse
    )

    tag_r2.append(
        fold_r2
    )


    print(
        f"\n第 {fold} 折："
    )

    print(
        f"MAE  = {fold_mae:.2f}"
    )

    print(
        f"RMSE = {fold_rmse:.2f}"
    )

    print(
        f"R²   = {fold_r2:.4f}"
    )


# ==============================
# 输出最终结果
# ==============================

print("\n" + "-" * 60)

print(
    "【加入 tag_list 后的 5 折交叉验证结果】"
)

print("-" * 60)


tag_mean_mae = np.mean(tag_mae)

tag_mean_rmse = np.mean(tag_rmse)

tag_mean_r2 = np.mean(tag_r2)

tag_std_r2 = np.std(tag_r2)


print(
    f"平均 MAE  = {tag_mean_mae:.2f}"
)

print(
    f"平均 RMSE = {tag_mean_rmse:.2f}"
)

print(
    f"平均 R²   = {tag_mean_r2:.4f}"
)

print(
    f"R² 标准差 = {tag_std_r2:.4f}"
)


# ==============================
# 和之前 Log Cost 模型比较
# ==============================

print("\n【模型对比】")

print(
    f"Log Cost 模型："
)

print(
    f"MAE={np.mean(log_mae):.2f}，"
    f"RMSE={np.mean(log_rmse):.2f}，"
    f"R²={np.mean(log_r2):.4f}"
)


print(
    f"\nLog Cost + tag_list 模型："
)

print(
    f"MAE={tag_mean_mae:.2f}，"
    f"RMSE={tag_mean_rmse:.2f}，"
    f"R²={tag_mean_r2:.4f}"
)


# ==============================
# 保存结果
# ==============================

tag_model_result = pd.DataFrame({
    "model": [
        "Log Cost Random Forest",
        "Log Cost Random Forest + tag_list"
    ],
    "MAE": [
        np.mean(log_mae),
        tag_mean_mae
    ],
    "RMSE": [
        np.mean(log_rmse),
        tag_mean_rmse
    ],
    "R2": [
        np.mean(log_r2),
        tag_mean_r2
    ]
})


tag_model_result.to_csv(
    "数据分析与机器学习/"
    "model_comparison.csv",
    index=False,
    encoding="utf-8-sig"
)


print("\n模型对比结果已经保存：")

print(
    "数据分析与机器学习/model_comparison.csv"
)


print("\nTag 特征模型测试完成！")

# ==============================
# 15. 最终模型特征重要性
# ==============================

print("\n" + "=" * 60)
print("生成最终模型特征重要性")
print("=" * 60)


# ==============================
# 使用全部 218 家商家训练最终模型
# ==============================

final_model = RandomForestRegressor(
    n_estimators=500,
    max_depth=6,
    min_samples_leaf=3,
    random_state=42
)


final_model.fit(
    X_with_tags,
    y_log
)


print("\n最终模型训练完成！")


# ==============================
# 计算特征重要性
# ==============================

final_importance = pd.DataFrame({
    "feature": X_with_tags.columns,
    "importance": final_model.feature_importances_
})


final_importance = (
    final_importance
    .sort_values(
        "importance",
        ascending=False
    )
    .reset_index(drop=True)
)


# ==============================
# 输出 Top 20
# ==============================

print("\n【最终模型 Top 20 特征重要性】")

print(
    final_importance
    .head(20)
    .to_string(index=False)
)


# ==============================
# 单独统计 tag 特征
# ==============================

tag_importance = final_importance[
    final_importance["feature"]
    .str.startswith("tag_")
].copy()


print("\n【Top 15 Tag 特征重要性】")

print(
    tag_importance
    .head(15)
    .to_string(index=False)
)


# ==============================
# 保存最终特征重要性
# ==============================

final_importance.to_csv(
    "数据分析与机器学习/"
    "final_feature_importance.csv",
    index=False,
    encoding="utf-8-sig"
)


print("\n最终特征重要性已经保存：")

print(
    "数据分析与机器学习/"
    "final_feature_importance.csv"
)


print("\n最终模型分析完成！")

print("\n分析完成！")