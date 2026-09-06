import pandas as pd
import folium

from folium.plugins import HeatMap


INPUT = r"D:\pycharm\PythonProject1\hz_food_multi_dim_viz\数据分析与机器学习\shop_cluster_result.csv"
OUTPUT = "../result/10_杭州餐饮密度热力图.html"


def generate_heatmap():

    df = pd.read_csv(INPUT)

    df = df[
        df["cat_level1"] == "餐饮服务"
    ].copy()


    location = df[
        "location"
    ].str.split(
        ",",
        expand=True
    )


    df["longitude"] = pd.to_numeric(
        location[0],
        errors="coerce"
    )

    df["latitude"] = pd.to_numeric(
        location[1],
        errors="coerce"
    )


    df = df.dropna(
        subset=[
            "longitude",
            "latitude"
        ]
    )


    m = folium.Map(
        location=[
            30.2741,
            120.1551
        ],
        zoom_start=11,
        tiles="CartoDB positron"
    )


    heat_data = df[
        [
            "latitude",
            "longitude"
        ]
    ].values.tolist()


    HeatMap(
        heat_data,
        radius=15,
        blur=20,
        min_opacity=0.3
    ).add_to(m)


    m.save(OUTPUT)


if __name__ == "__main__":
    generate_heatmap()