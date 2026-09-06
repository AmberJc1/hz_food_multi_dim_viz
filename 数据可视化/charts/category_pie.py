import pandas as pd
import matplotlib.pyplot as plt

from theme import set_theme, get_colors


set_theme()

colors = get_colors()


df = pd.read_csv(
    "../statistics_result/category_count.csv"
)


plt.figure(figsize=(8, 8))


plt.pie(
    df["shop_count"],
    labels=df["category"],
    autopct="%1.1f%%",
    startangle=90,
    colors=colors[:len(df)],
    wedgeprops={
        "edgecolor": "#F7F5F1",
        "linewidth": 2
    }
)


plt.title(
    "杭州餐饮品类占比分布",
    fontsize=18,
    pad=20
)


plt.tight_layout()


plt.savefig(
    "../result/02_餐饮品类占比.png",
    bbox_inches="tight"
)


plt.close()