import streamlit as st
import sys
sys.path.append("./src")
from database import ShopDB

db = ShopDB()
all_data = db.query_shop()

st.title("🍜杭州餐饮商家数据筛选查询")

with st.sidebar:
    st.header("筛选条件")
    district_list = ["全部"] + sorted(all_data["adname"].dropna().unique().tolist())
    sel_district = st.selectbox("选择行政区", district_list)

    cost_list = ["全部"] + sorted(all_data["cost_level"].dropna().unique().tolist())
    sel_cost = st.selectbox("消费等级", cost_list)

def trans_param(val):
    return None if val == "全部" else val

result_df = db.query_shop(
    district=trans_param(sel_district),
    cost_level=trans_param(sel_cost)
)

st.subheader(f"筛选结果：共 {len(result_df)} 条数据")
st.dataframe(result_df)
