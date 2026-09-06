import pandas as pd


INPUT = r"D:\pycharm\PythonProject1\hz_food_multi_dim_viz\数据分析与机器学习\shop_cluster_result.csv"
OUTPUT = "../statistics_result/correlation_matrix.csv"


def generate_statistics():

    df = pd.read_csv(INPUT)

    # 消费缺失数据不参与价格相关性分析
    df.loc[
        df["cost_missing"] == True,
        "cost"
    ] = pd.NA

    # 评分缺失数据不参与评分相关性分析
    df.loc[
        df["rating_missing"] == True,
        "rating"
    ] = pd.NA

    columns = [
        "rating",
        "cost",
        "favorite_num",
        "cluster"
    ]

    for col in columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    result = df[
        columns
    ].corr()

    result.to_csv(
        OUTPUT,
        encoding="utf-8-sig"
    )


if __name__ == "__main__":
    generate_statistics()