import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


# ==============================
# 莫兰迪色系
# ==============================

MORANDI_COLORS = [
    "#8FA3BF",  # 灰蓝
    "#A8B5A2",  # 灰绿
    "#C8B6A6",  # 奶茶
    "#D8B4A0",  # 杏粉
    "#B7B7A4",  # 米灰
    "#9C9B8F",  # 灰褐
    "#A7A6BA",  # 灰紫
    "#C4B7A6",  # 米棕
]


def set_theme():

    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS"
    ]

    plt.rcParams["axes.unicode_minus"] = False

    plt.rcParams["figure.dpi"] = 150

    plt.rcParams["savefig.dpi"] = 200

    plt.rcParams["axes.facecolor"] = "#F7F5F1"

    plt.rcParams["figure.facecolor"] = "#F7F5F1"

    plt.rcParams["axes.edgecolor"] = "#B8B5AE"

    plt.rcParams["axes.labelcolor"] = "#555555"

    plt.rcParams["xtick.color"] = "#666666"

    plt.rcParams["ytick.color"] = "#666666"

    plt.rcParams["text.color"] = "#4F4F4F"

    plt.rcParams["axes.titleweight"] = "bold"


def get_colors():

    return MORANDI_COLORS


def get_cmap():

    return LinearSegmentedColormap.from_list(
        "morandi",
        MORANDI_COLORS
    )