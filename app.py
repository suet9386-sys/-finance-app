import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os
import uuid

st.set_page_config(page_title="个人记账系统", layout="wide")

DATA_PATH = "data/finance.csv"

if not os.path.exists(DATA_PATH):
    df = pd.DataFrame(columns=["id","date","type","category","payment","amount","note"])
    df.to_csv(DATA_PATH,index=False)

df = pd.read_csv(DATA_PATH)

st.title("📊 小雷帮你记")

menu = st.sidebar.selectbox(
"功能菜单",
["新增记录","查看账单","统计分析","月度报告"]
)

# 新增记录
if menu == "新增记录":

    st.subheader("新增一笔")

    col1,col2 = st.columns(2)

    with col1:
        record_date = st.date_input("日期",date.today())

        record_type = st.selectbox(
        "类型",
        ["支出","收入"]
        )

        category = st.selectbox(
        "分类",
        ["早餐","午餐","晚餐","零食","购物","交通","娱乐","工资","其他"]
        )

    with col2:
        payment = st.selectbox(
        "支付方式",
        ["微信","支付宝","花呗","现金","银行卡"]
        )

        amount = st.number_input("金额",min_value=0.0)

        note = st.text_input("备注")

    if st.button("保存记录"):

        new_data = pd.DataFrame([{
        "id":str(uuid.uuid4()),
        "date":record_date,
        "type":record_type,
        "category":category,
        "payment":payment,
        "amount":amount,
        "note":note
        }])

        df = pd.concat([df,new_data])

        df.to_csv(DATA_PATH,index=False)

        st.success("记录成功!")

# 查看账单
if menu == "查看账单":

    st.subheader("账单管理")

    st.dataframe(df)

    delete_id = st.text_input("输入要删除的ID")

    if st.button("删除记录"):

        df = df[df["id"] != delete_id]

        df.to_csv(DATA_PATH,index=False)

        st.success("删除成功")

# 统计分析
if menu == "统计分析":

    expense = df[df["type"]=="支出"]

    if len(expense) > 0:

        st.subheader("消费分类")

        category_sum = expense.groupby("category")["amount"].sum().reset_index()

        fig = px.pie(
        category_sum,
        values="amount",
        names="category"
        )

        st.plotly_chart(fig)

        st.subheader("消费趋势")

        trend = expense.groupby("date")["amount"].sum().reset_index()

        fig2 = px.line(
        trend,
        x="date",
        y="amount"
        )

        st.plotly_chart(fig2)

# 月度报告
if menu == "月度报告":

    st.subheader("本月消费报告")

    df["date"] = pd.to_datetime(df["date"])

    month = date.today().month

    month_data = df[df["date"].dt.month == month]

    expense = month_data[month_data["type"]=="支出"]

    income = month_data[month_data["type"]=="收入"]

    total_expense = expense["amount"].sum()
    total_income = income["amount"].sum()

    st.metric("本月支出", total_expense)
    st.metric("本月收入", total_income)

    if total_expense > 0:

        category_sum = expense.groupby("category")["amount"].sum().reset_index()

        fig = px.bar(
        category_sum,
        x="category",
        y="amount",
        title="本月消费分类"
        )

        st.plotly_chart(fig)