import pandas as pd
import sys
sys.path.append("../")

from src.data_cleaner import DataCleaner

if __name__ == "__main__":
    raw_df = pd.read_csv("../data/raw/hangzhou_catering_combined.csv", encoding="utf-8-sig")

    cleaner = DataCleaner(raw_df, cost_quantile=0.99)
    clean_df = (cleaner.drop_duplicate_shop()
                .handle_missing()
                .filter_abnormal()
                .standard_district()
                .parse_type_category()
                .parse_atag_tags()
                .merge_main_category()
                .get_clean_data())

    out_path = "../data/processed/hangzhou_clean.csv"
    clean_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\n清洗完成：{out_path}")
