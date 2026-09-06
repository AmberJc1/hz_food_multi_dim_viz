import pandas as pd
import matplotlib.pyplot as plt

from theme import set_theme, get_colors


set_theme()
colors = get_colors()


df = pd.read_csv(
    "../statistics_result/district_count.csv"
)


plt.figure(figsize=(10, 6))

bars = plt.bar(
    df["adname"],
    df["shop_count"],
    color=colors[0],
    width=0.65
)


plt.title(
    "杭州各行政区餐饮商家数量",
    fontsize=18,
    pad=15
)

plt.xlabel("行政区")
plt.ylabel("商家数量")

plt.xticks(rotation=40)


# 添加数据标签
for bar in bars:

    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        str(int(height)),
        ha="center",
        va="bottom",
        fontsize=9
    )


plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)


plt.tight_layout()

plt.savefig(
    "../result/01_行政区商家数量.png",
    bbox_inches="tight"
)

plt.close()