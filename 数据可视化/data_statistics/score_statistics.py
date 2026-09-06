import pandas as pd



def score_cost(input_file,output_file):


    df=pd.read_csv(input_file)



    result=df[
        [
            "cost",
            "score"
        ]
    ]


    result.to_csv(

        output_file,

        index=False,

        encoding="utf-8-sig"

    )


if __name__=="__main__":


    score_cost(

        "../../数据分析与机器学习/cost_prediction_dataset.csv",

        "../statistics_result/score_cost.csv"

    )