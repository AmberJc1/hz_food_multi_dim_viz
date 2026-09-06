# -*- coding: UTF-8 -*-
"""
@Project ：program
@File    ：shop7.py
@IDE     ：PyCharm
@Author  ：cxy
@Date    ：2026/9/6 20:00
@Brief   ：
"""
# -*- coding: UTF-8 -*-
"""
@Project ：program
@File    ：shop7.py
@IDE     ：PyCharm
@Author  ：cxy
@Date    ：2026/9/6 17:03
@Brief   ：基于已有 CSV 继续补全空缺的评分和人均消费
"""
import pandas as pd
import requests
import time
import os

API_KEY = "a0c23cb924e35d40f3452b3f69fc0d3d"  # 替换为有效Key

# ==================== 获取 POI 详情（带类型转换） ====================
def fetch_poi_detail(poi_id):
    """
    获取单个POI的评分和人均消费，失败重试3次
    返回 (rating, cost) 均为 float 或 None
    """
    url = "https://restapi.amap.com/v3/place/detail"
    params = {"key": API_KEY, "id": poi_id}
    retries = 3
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=15)
            data = resp.json()
            if data.get("status") == "1" and data.get("pois"):
                poi = data["pois"][0]
                biz_ext = poi.get("biz_ext", {})

                # ---- 提取评分 ----
                rating_str = biz_ext.get("rating")
                rating = None
                if rating_str is not None and rating_str != "":
                    try:
                        rating = float(rating_str)
                    except (ValueError, TypeError):
                        rating = None

                # ---- 提取人均消费 ----
                cost_val = biz_ext.get("cost")
                cost = None
                if isinstance(cost_val, list) and len(cost_val) > 0:
                    cost_str = cost_val[0]
                    try:
                        cost = float(cost_str)
                    except (ValueError, TypeError):
                        cost = None
                elif isinstance(cost_val, (str, int, float)):
                    try:
                        cost = float(cost_val)
                    except (ValueError, TypeError):
                        cost = None

                return rating, cost
            else:
                print(f"API错误: {data.get('info')}，ID: {poi_id}")
                return None, None
        except requests.exceptions.Timeout:
            print(f"⏱️ 超时 (尝试 {attempt+1}/{retries})，等待后重试...")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ 未知错误: {e}，ID: {poi_id}")
            return None, None
    print(f"❌ 店铺 {poi_id} 重试 {retries} 次后仍失败，跳过")
    return None, None

# ==================== 主程序 ====================
# 1. 读取现有的 CSV 文件（即已部分补全的文件）
input_file = "hangzhou_catering_combined_filled.csv"   # 你已有的文件
if not os.path.exists(input_file):
    # 如果文件不存在，则从原始文件开始（可选）
    input_file = "hangzhou_catering_combined (1).csv"
    print(f"⚠️ 未找到 {input_file}，将从原始文件开始")

df = pd.read_csv(input_file)

# 2. 确保 rating 和 cost 列是 float 类型，无法转换的设为 NaN
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["cost"] = pd.to_numeric(df["cost"], errors="coerce")

# 3. 找出空缺行（rating 或 cost 为 NaN）
need_fill = df[df["rating"].isna() | df["cost"].isna()]
print(f"需要补全的店铺数：{len(need_fill)}")

if len(need_fill) == 0:
    print("✅ 所有空缺已补全，无需操作")
    exit()

# 4. （可选）断点续传：读取已处理ID文件，跳过已请求但可能未写入成功的ID
# 这里我们可以不依赖外部文件，因为每次运行都会从当前CSV中识别空缺。
# 但为了更安全，可以维护一个 processed_ids.txt 来记录已经补全成功的ID，
# 不过由于我们实时保存，中断后再次运行空缺行会减少，所以不需要额外记录。

# 5. 开始处理
total = len(need_fill)
completed = 0
failed = 0

for count, (idx, row) in enumerate(need_fill.iterrows(), start=1):
    poi_id = row["id"]
    print(f"正在处理第 {count}/{total} 个，ID={poi_id}")
    rating, cost = fetch_poi_detail(poi_id)

    if rating is not None or cost is not None:
        if rating is not None:
            df.at[idx, "rating"] = rating
        if cost is not None:
            df.at[idx, "cost"] = cost
        completed += 1
    else:
        failed += 1
        print(f"⏭️ 跳过ID {poi_id}（未获取到评分和消费）")

    # 每处理10条保存一次中间结果（防止意外中断丢失大量进度）
    if count % 10 == 0:
        df.to_csv("hangzhou_catering_combined_filled_temp.csv", index=False, encoding="utf-8-sig")
        print(f"💾 已保存中间进度，已完成 {count}/{total}")

    time.sleep(0.5)  # 控制请求频率

# 6. 最终保存（覆盖原文件或保存为新文件）
df.to_csv("hangzhou_catering_combined_filled2.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ 全部完成！成功补全 {completed} 个，失败 {failed} 个。")
print(f"📁 结果已保存至 hangzhou_catering_combined_filled2.csv")