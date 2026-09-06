import pandas as pd


def generate_score_cost_data(
        input_file,
        output_file
):

    # 读取数据
    df = pd.read_csv(
        input_file
    )


    # 删除消费缺失数据
    df = df[
        df["cost_missing"] != True
    ]


    # 只保留需要字段
    result = df[
        [
            "cost",
            "rating"
        ]
    ]


    # 删除空值
    result = result.dropna()


    # 确保类型正确

    result["cost"] = pd.to_numeric(
        result["cost"],
        errors="coerce"
    )


    result["rating"] = pd.to_numeric(
        result["rating"],
        errors="coerce"
    )


    # 再次删除异常空值

    result = result.dropna()



    # 计算相关系数

    correlation = result[
        [
            "cost",
            "rating"
        ]
    ].corr().iloc[0,1]



    print(
        "价格与评分相关系数:",
        round(correlation,3)
    )



    # 保存统计数据

    result.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )



if __name__=="__main__":


    generate_score_cost_data(

        "../../数据分析与机器学习/shop_cluster_result.csv",

        "../statistics_result/score_cost_relation.csv"

    )