import pandas as pd
import os


INPUT = r"D:\pycharm\PythonProject1\hz_food_multi_dim_viz\数据分析与机器学习\shop_cluster_result.csv"
OUTPUT = "../statistics_result/category_count.csv"


def classify_category(tag):

    if pd.isna(tag):
        return "其他"

    tag = str(tag)

    if any(x in tag for x in [
        "火锅"
    ]):
        return "火锅"

    if any(x in tag for x in [
        "烧烤"
    ]):
        return "烧烤"

    if any(x in tag for x in [
        "日本",
        "日料",
        "寿司"
    ]):
        return "日料"

    if any(x in tag for x in [
        "西餐",
        "牛排"
    ]):
        return "西餐"

    if any(x in tag for x in [
        "咖啡"
    ]):
        return "咖啡"

    if any(x in tag for x in [
        "奶茶",
        "茶饮"
    ]):
        return "茶饮"

    if any(x in tag for x in [
        "甜品",
        "蛋糕",
        "烘焙"
    ]):
        return "甜品"

    if any(x in tag for x in [
        "小吃",
        "快餐",
        "面馆",
        "粉"
    ]):
        return "小吃快餐"

    if any(x in tag for x in [
        "中餐",
        "江浙",
        "川菜",
        "湘菜",
        "粤菜",
        "浙菜",
        "东北",
        "徽菜",
        "闽菜"
    ]):
        return "中餐"

    return "其他"


def generate_statistics():

    df = pd.read_csv(INPUT)

    df = df[
        df["cat_level1"] == "餐饮服务"
    ]

    df["category"] = df["keytag"].apply(
        classify_category
    )

    result = (
        df.groupby("category")
        .size()
        .reset_index(name="shop_count")
    )

    total = result["shop_count"].sum()

    result["percentage"] = (
        result["shop_count"] / total * 100
    ).round(2)

    result = result.sort_values(
        "shop_count",
        ascending=False
    )

    os.makedirs(
        "../数据可视化/statistics_result",
        exist_ok=True
    )

    result.to_csv(
        OUTPUT,
        index=False,
        encoding="utf-8-sig"
    )


if __name__ == "__main__":
    generate_statistics()