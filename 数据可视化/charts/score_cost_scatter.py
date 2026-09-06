import pandas as pd
import matplotlib.pyplot as plt


from theme import set_theme,get_colors


set_theme()


# 读取统计结果

df=pd.read_csv(
    "../statistics_result/score_cost_relation.csv"
)



plt.figure(
    figsize=(8,5)
)



plt.scatter(

    df["cost"],

    df["rating"],

    color=get_colors()[3],

    alpha=0.6,

    s=35

)



plt.xlabel(
    "人均消费金额(cost)"
)


plt.ylabel(
    "用户评分(rating)"
)


plt.title(
    "餐饮消费水平与评分关系分析"
)



# 添加趋势线

import numpy as np


z=np.polyfit(
    df["cost"],
    df["rating"],
    1
)


p=np.poly1d(z)


plt.plot(

    df["cost"],

    p(df["cost"]),

    color=get_colors()[0],

    linewidth=2

)



plt.savefig(

    "../result/05_评分消费关系.png",

    bbox_inches="tight"

)


plt.close()