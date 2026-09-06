import pandas as pd
import matplotlib.pyplot as plt

from theme import set_theme, get_cmap


set_theme()


df = pd.read_csv(
    "../statistics_result/correlation_matrix.csv",
    index_col=0
)


plt.figure(figsize=(8, 7))


plt.imshow(
    df,
    cmap=get_cmap(),
    aspect="auto",
    vmin=-1,
    vmax=1
)


plt.colorbar(
    label="Pearson相关系数"
)


plt.xticks(
    range(len(df.columns)),
    df.columns
)

plt.yticks(
    range(len(df.index)),
    df.index
)


for i in range(len(df.index)):

    for j in range(len(df.columns)):

        plt.text(
            j,
            i,
            f"{df.iloc[i, j]:.2f}",
            ha="center",
            va="center",
            fontsize=10
        )


plt.title(
    "餐饮商家指标相关性热力图",
    fontsize=18
)


plt.tight_layout()


plt.savefig(
    "../result/06_相关性热力图.png",
    bbox_inches="tight"
)


plt.close()