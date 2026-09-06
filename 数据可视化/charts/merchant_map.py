import pandas as pd
import folium
import os
import html

# ==================================================
# 1. 文件路径
# ==================================================
INPUT = r"D:\pycharm\PythonProject1\hz_food_multi_dim_viz\数据分析与机器学习\shop_cluster_result.csv"

OUTPUT = "../result/09_杭州市餐饮商家地图.html"

# ==================================================
# 2. 读取数据
# ==================================================
df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)

# 清理字段名
df.columns = df.columns.str.strip()

print("当前数据字段：")
print(df.columns.tolist())

# ==================================================
# 3. 只保留餐饮服务
# ==================================================
df = df[
    df["cat_level1"].astype(str).str.strip() == "餐饮服务"
].copy()

# ==================================================
# 4. 处理 rating 和 cost
# ==================================================
if "rating" in df.columns:
    df["rating"] = pd.to_numeric(
        df["rating"],
        errors="coerce"
    )

if "cost" in df.columns:
    df["cost"] = pd.to_numeric(
        df["cost"],
        errors="coerce"
    )

# ==================================================
# 5. 处理经纬度
# ==================================================
location = (
    df["location"]
    .astype(str)
    .str.strip()
    .str.split(",", expand=True)
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

print("\n有效地图商家数量：", len(df))

# ==================================================
# 6. 创建地图
# ==================================================
m = folium.Map(
    location=[
        30.2741,
        120.1551
    ],
    zoom_start=11,
    tiles="CartoDB positron"
)

# ==================================================
# 7. 添加商家
# ==================================================
for _, row in df.iterrows():

    # ==================================================
    # 商家名称
    # ==================================================
    name = row.get("name", "")

    if pd.isna(name):
        name = "未知商家"
    else:
        name = str(name).strip()

    name = html.escape(name)

    info_html = ""

    # --------------------------------------------------
    # 评分
    # --------------------------------------------------
    if (
        "rating" in df.columns
        and pd.notna(row["rating"])
    ):
        rating = float(row["rating"])

        info_html += f"""
        <div style="margin-bottom:5px;">
            ⭐ <b>评分：</b>
            <span style="
                color:#8FA3BF;
                font-weight:bold;
            ">
                {rating:.1f} 分
            </span>
        </div>
        """

    # --------------------------------------------------
    # 平均消费
    # --------------------------------------------------
    if (
        "cost" in df.columns
        and pd.notna(row["cost"])
    ):
        cost = float(row["cost"])

        info_html += f"""
        <div style="margin-bottom:5px;">
            💰 <b>平均消费：</b>
            <span style="
                color:#A68A7B;
                font-weight:bold;
            ">
                ¥{cost:.0f} / 人
            </span>
        </div>
        """

    # --------------------------------------------------
    # 餐饮品类
    # --------------------------------------------------
    category = row.get("keytag", "")

    if pd.notna(category) and str(category).strip():
        category = html.escape(str(category).strip())

        info_html += f"""
        <div style="margin-bottom:5px;">
            🍜 <b>餐饮品类：</b>
            {category}
        </div>
        """

    # --------------------------------------------------
    # 所属区域
    # --------------------------------------------------
    district = row.get("adname", "")

    if pd.notna(district) and str(district).strip():
        district = html.escape(str(district).strip())

        info_html += f"""
        <div style="margin-bottom:5px;">
            📍 <b>所属区域：</b>
            {district}
        </div>
        """

    # --------------------------------------------------
    # 地址
    # --------------------------------------------------
    address = row.get("address", "")

    if pd.notna(address) and str(address).strip():
        address = html.escape(str(address).strip())

        info_html += f"""
        <div style="margin-bottom:5px;">
            🏠 <b>地址：</b>
            {address}
        </div>
        """

    # ==================================================
    # Popup
    # ==================================================
    popup_html = f"""
    <div style="
        width:300px;
        font-family:'Microsoft YaHei',Arial;
        font-size:14px;
        line-height:1.8;
    ">

        <div style="
            font-size:18px;
            font-weight:bold;
            color:#65758B;
            margin-bottom:10px;
        ">
            {name}
        </div>

        <hr style="
            border:0;
            border-top:1px solid #eeeeee;
            margin:5px 0 10px 0;
        ">

        {info_html}

    </div>
    """

    # ==================================================
    # 地图点
    # ==================================================
    folium.CircleMarker(
        location=[
            row["latitude"],
            row["longitude"]
        ],
        radius=5,

        popup=folium.Popup(
            popup_html,
            max_width=350
        ),

        tooltip=name,

        color="#8FA3BF",

        fill=True,

        fill_color="#8FA3BF",

        fill_opacity=0.75

    ).add_to(m)

# ==================================================
# 8. 保存地图
# ==================================================
os.makedirs(
    os.path.dirname(OUTPUT),
    exist_ok=True
)

m.save(OUTPUT)

print("\n===================================")
print("地图生成完成！")
print("===================================")
print("商家数量：", len(df))
print("地图文件：", OUTPUT)
print("===================================")
