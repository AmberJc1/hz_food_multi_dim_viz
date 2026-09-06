import pandas as pd
import matplotlib.pyplot as plt

from theme import set_theme, get_colors


set_theme()

colors = get_colors()


df = pd.read_csv(
    "../../数据分析与机器学习/cluster_profile.csv"
)


plt.figure(figsize=(10, 6))


bars = plt.bar(
    df["cluster_name"],
    df["shop_count"],
    color=colors[:len(df)]
)


plt.title(
    "餐饮商家聚类群体规模分析",
    fontsize=18
)

plt.xlabel("商家群体")
plt.ylabel("商家数量")


plt.xticks(
    rotation=20
)


for bar in bars:

    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        str(int(height)),
        ha="center",
        va="bottom"
    )


plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)


plt.tight_layout()


plt.savefig(
    "../result/07_商家聚类分析.png",
    bbox_inches="tight"
)


plt.close()