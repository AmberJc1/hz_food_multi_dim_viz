import pandas as pd


def district_count(input_file,output_file):

    df=pd.read_csv(input_file)


    result=df.groupby(
        "adname"
    ).size().reset_index(
        name="shop_count"
    )


    result=result.sort_values(
        "shop_count",
        ascending=False
    )


    result.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )


if __name__=="__main__":

    district_count(
        "../../数据分析与机器学习/shop_cluster_result.csv",
        "../statistics_result/district_count.csv"
    )