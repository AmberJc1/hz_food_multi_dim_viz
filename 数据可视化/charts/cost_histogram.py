import pandas as pd
import matplotlib.pyplot as plt

from theme import set_theme, get_colors


set_theme()

colors = get_colors()


df = pd.read_csv(
    "../statistics_result/price_distribution.csv"
)


plt.figure(figsize=(9, 6))


plt.hist(
    df["cost"],
    bins=25,
    color=colors[2],
    edgecolor="#F7F5F1",
    alpha=0.9
)


plt.title(
    "餐饮商家人均消费价格分布",
    fontsize=18
)

plt.xlabel("人均消费金额（元）")
plt.ylabel("商家数量")


plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)


plt.tight_layout()


plt.savefig(
    "../result/03_消费价格分布.png",
    bbox_inches="tight"
)


plt.close()