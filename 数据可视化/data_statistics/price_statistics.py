import pandas as pd



def price_statistics(input_file,output_file):


    df=pd.read_csv(input_file)


    result=df[
        ["cost"]
    ].describe()


    result.to_csv(
        output_file,
        encoding="utf-8-sig"
    )


if __name__=="__main__":


    price_statistics(

        "../../数据分析与机器学习/shop_cluster_result.csv",

        "../statistics_result/price_distribution.csv"

    )