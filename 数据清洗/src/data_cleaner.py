# src/data_cleaner.py
import pandas as pd
import numpy as np


class DataCleaner:
    def __init__(self, df: pd.DataFrame,
                 cost_quantile=0.99):
        self.df = df.copy()
        self.cost_quantile = cost_quantile
        self._origin_rows = len(self.df)
        print(f"[初始化] 原始数据行数: {self._origin_rows}")

    def drop_duplicate_shop(self):
        before = len(self.df)
        self.df = self.df.drop_duplicates(subset=["id"], keep="first")
        after = len(self.df)
        print(f"[去重] 处理前:{before},处理后:{after},删除:{before-after}")
        return self

    def handle_missing(self):
        before = len(self.df)
        self.df["cost"] = self.df["cost"].replace("[]", np.nan)
        self.df["cost"] = pd.to_numeric(self.df["cost"], errors="coerce")
        self.df["rating"] = pd.to_numeric(self.df["rating"], errors="coerce")

        self.df["cost_missing"] = self.df["cost"].isna()
        self.df["rating_missing"] = self.df["rating"].isna()
        self.df["rating_is_zero"] = self.df["rating"] == 0

        # 建模可用标记：同时有有效评分>0、有人均消费
        self.df["valid_for_model"] = (~self.df["cost_missing"]) & (~self.df["rating_missing"]) & (self.df["rating"] > 0)

        self.df["tel"] = self.df["tel"].fillna("未知")
        self.df["address"] = self.df["address"].fillna("地址未获取")

        after = len(self.df)
        print(f"[缺失处理] 处理前:{before},处理后:{after},删除:{before-after}")
        print(f"可用于建模样本数量(valid_for_model=True): {self.df['valid_for_model'].sum()}")
        return self

    def filter_abnormal(self):
        before = len(self.df)
        # 只剔除负分，空、0‑5全部保留
        rating_mask = (self.df["rating"] >= 0) | self.df["rating"].isna()
        self.df = self.df[rating_mask]

        valid_cost_mask = ~self.df["cost_missing"]
        if valid_cost_mask.sum() > 0:
            upper_cost = self.df.loc[valid_cost_mask, "cost"].quantile(self.cost_quantile)
            print(f"[cost分位数过滤] {self.cost_quantile}分位数，价格上限:{round(upper_cost,2)}")
            price_ok = ((self.df["cost"] > 0) & (self.df["cost"] <= upper_cost)) | self.df["cost_missing"]
            self.df = self.df[price_ok]

        after = len(self.df)
        print(f"[异常过滤] 处理前:{before},处理后:{after},删除:{before-after}")
        return self

    def standard_district(self):
        district_map = {
            "上城区": "上城区",
            "拱墅区": "拱墅区",
            "西湖区": "西湖区",
            "滨江区": "滨江区",
            "萧山区": "萧山区",
            "余杭区": "余杭区",
            "临平区": "临平区",
            "钱塘区": "钱塘区",
            "富阳区": "富阳区",
            "临安区": "临安区",
            "桐庐县": "桐庐县",
            "淳安县": "淳安县",
            "建德市": "建德市"
        }
        self.df["adname"] = self.df["adname"].map(district_map).fillna(self.df["adname"])
        print("[行政区标准化完成]")
        return self

    def parse_type_category(self):

        self.df["type_main"] = self.df["type"].fillna("").str.split("|").str[0]
        split_df = self.df["type_main"].str.split(";", expand=True)
        self.df["cat_level1"] = split_df[0].fillna("")
        self.df["cat_level2"] = split_df[1].fillna("")
        print("[type分类解析完成：生成cat_level1 cat_level2]")
        return self

    def parse_atag_tags(self):
        def split_tag(text):
            if pd.isna(text) or text == "[]" or text == "":
                return []
            return [t.strip() for t in str(text).split(",") if t.strip()]
        self.df["tag_list"] = self.df["atag"].apply(split_tag)
        print("[atag标签解析完成，生成tag_list列表字段]")
        return self

    def merge_main_category(self):
        """基于cat_level2做大类映射，cat_level2已经是字符串不会出现nan问题"""
        def map_main(l2_text):
            l2 = str(l2_text).strip()
            if "火锅" in l2:
                return "火锅"
            elif "咖啡" in l2 or "奶茶" in l2:
                return "饮品甜点"
            elif "浙江菜" in l2 or "江浙菜" in l2:
                return "江浙本帮菜"
            elif "西餐" in l2:
                return "西餐"
            elif "日本料理" in l2 or "韩国料理" in l2:
                return "日韩料理"
            else:
                return "其他餐饮"
        self.df["main_category"] = self.df["cat_level2"].apply(map_main)
        print("[业务大类main_category生成完成]")
        return self

    def get_clean_data(self) -> pd.DataFrame:
        print(f"[清洗全部结束] 原始:{self._origin_rows}，清洗后总数据行数: {len(self.df)}")
        print(f"标记可建模样本数 valid_for_model=True：{self.df['valid_for_model'].sum()}")
        return self.df
