import pandas as pd
import matplotlib.pyplot as plt

from theme import set_theme, get_colors


set_theme()

colors = get_colors()


df = pd.read_csv(
    "../statistics_result/price_distribution.csv"
)


plt.figure(figsize=(7, 6))


plt.boxplot(
    df["cost"],
    vert=True,
    patch_artist=True,
    boxprops={
        "facecolor": colors[4],
        "color": "#777777"
    },
    medianprops={
        "color": "#555555",
        "linewidth": 2
    },
    whiskerprops={
        "color": "#777777"
    },
    capprops={
        "color": "#777777"
    },
    flierprops={
        "marker": "o",
        "markersize": 4,
        "markerfacecolor": colors[3],
        "alpha": 0.5
    }
)


plt.title(
    "餐饮商家消费价格箱线图",
    fontsize=18
)

plt.ylabel(
    "人均消费金额（元）"
)


plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)


plt.tight_layout()


plt.savefig(
    "../result/04_消费价格箱线图.png",
    bbox_inches="tight"
)


plt.close()