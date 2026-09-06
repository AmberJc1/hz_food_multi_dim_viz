import pandas as pd
import matplotlib.pyplot as plt

from theme import set_theme, get_colors


set_theme()

colors = get_colors()


df = pd.read_csv(
    "../../数据分析与机器学习/final_feature_importance.csv"
)


df = df.sort_values(
    "importance",
    ascending=False
).head(15)


df = df.sort_values(
    "importance"
)


plt.figure(figsize=(10, 7))


plt.barh(
    df["feature"],
    df["importance"],
    color=colors[0]
)


plt.title(
    "消费预测模型特征重要性",
    fontsize=18
)

plt.xlabel("特征重要性")
plt.ylabel("特征")


plt.grid(
    axis="x",
    linestyle="--",
    alpha=0.3
)


plt.tight_layout()


plt.savefig(
    "../result/08_特征重要性.png",
    bbox_inches="tight"
)


plt.close()