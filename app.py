import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import uuid
import os
import re

# --------------------
# 页面配置（手机友好）
# --------------------

st.set_page_config(
    page_title="AI记账",
    page_icon="💰",
    layout="wide"
)

# --------------------
# 预算
# --------------------

MONTHLY_BUDGET = 3000

DATA_PATH = "finance.csv"

# --------------------
# 创建数据库
# --------------------

if not os.path.exists(DATA_PATH):

    df_init = pd.DataFrame(columns=[
        "id","date","type","category","payment","amount","note"
    ])

    df_init.to_csv(DATA_PATH,index=False)

# --------------------
# 读取数据
# --------------------

try:
    df = pd.read_csv(DATA_PATH,encoding="utf-8")
except:
    df = pd.read_csv(DATA_PATH,encoding="gbk")

# --------------------
# AI解析
# --------------------

def parse_text(text):

    amount = 0
    category = "其他"
    record_type = "支出"

    nums = re.findall(r"\d+\.?\d*", text)

    if nums:
        amount = float(nums[0])

    if "早餐" in text:
        category = "早餐"

    elif "午餐" in text:
        category = "午餐"

    elif "晚餐" in text:
        category = "晚餐"

    elif "交通" in text:
        category = "交通"

    elif "购物" in text:
        category = "购物"

    elif "娱乐" in text:
        category = "娱乐"

    elif "工资" in text:
        category = "工资"
        record_type = "收入"

    return amount,category,record_type

# --------------------
# UI
# --------------------

st.title("💰 AI智能记账")

menu = st.sidebar.selectbox(
    "菜单",
    [
        "AI快速记账",
        "新增记录",
        "账单记录",
        "统计分析",
        "月度报告"
    ]
)

# --------------------
# AI记账
# --------------------

if menu == "AI快速记账":

    st.subheader("AI快速记账")

    text = st.text_input("输入，例如：20 午餐")

    if st.button("解析并保存"):

        amount,category,record_type = parse_text(text)

        st.write("金额:",amount)
        st.write("分类:",category)
        st.write("类型:",record_type)

        new_data = pd.DataFrame([{
            "id":str(uuid.uuid4()),
            "date":str(date.today()),
            "type":record_type,
            "category":category,
            "payment":"微信",
            "amount":amount,
            "note":text
        }])

        df2 = pd.concat([df,new_data])

        df2.to_csv(DATA_PATH,index=False)

        st.success("记录成功")

# --------------------
# 手动记账
# --------------------

if menu == "新增记录":

    st.subheader("新增记录")

    col1,col2 = st.columns(2)

    with col1:

        record_date = st.date_input("日期",date.today())

        record_type = st.selectbox(
            "类型",
            ["支出","收入"]
        )

        category = st.selectbox(
            "分类",
            [
                "早餐","午餐","晚餐",
                "购物","交通","娱乐",
                "工资","其他"
            ]
        )

    with col2:

        payment = st.selectbox(
            "支付方式",
            [
                "微信","支付宝",
                "花呗","银行卡","现金"
            ]
        )

        amount = st.number_input(
            "金额",
            min_value=0.0
        )

        note = st.text_input("备注")

    if st.button("保存记录"):

        new_data = pd.DataFrame([{
            "id":str(uuid.uuid4()),
            "date":str(record_date),
            "type":record_type,
            "category":category,
            "payment":payment,
            "amount":amount,
            "note":note
        }])

        df2 = pd.concat([df,new_data])

        df2.to_csv(DATA_PATH,index=False)

        st.success("保存成功")

# --------------------
# 账单记录
# --------------------

if menu == "账单记录":

    st.subheader("全部账单")

    st.dataframe(df)

    if st.button("导出Excel"):

        file_name = "finance_report.xlsx"

        df.to_excel(file_name,index=False)

        with open(file_name,"rb") as f:

            st.download_button(
                "下载Excel",
                f,
                file_name=file_name
            )

# --------------------
# 统计分析
# --------------------

if menu == "统计分析":

    st.subheader("消费统计")

    expense = df[df["type"]=="支出"]

    if len(expense)>0:

        category_sum = expense.groupby(
            "category"
        )["amount"].sum().reset_index()

        fig = px.pie(
            category_sum,
            values="amount",
            names="category",
            title="消费分类"
        )

        st.plotly_chart(fig)

        trend = expense.groupby(
            "date"
        )["amount"].sum().reset_index()

        fig2 = px.line(
            trend,
            x="date",
            y="amount",
            title="消费趋势"
        )

        st.plotly_chart(fig2)

# --------------------
# 月度报告
# --------------------

if menu == "月度报告":

    st.subheader("本月报告")

    df["date"] = pd.to_datetime(df["date"])

    month = date.today().month

    month_data = df[df["date"].dt.month==month]

    expense = month_data[month_data["type"]=="支出"]

    income = month_data[month_data["type"]=="收入"]

    total_expense = expense["amount"].sum()

    total_income = income["amount"].sum()

    col1,col2 = st.columns(2)

    with col1:
        st.metric("本月支出",total_expense)

    with col2:
        st.metric("本月收入",total_income)

    # 预算

    budget_left = MONTHLY_BUDGET - total_expense

    st.subheader("预算情况")

    col3,col4 = st.columns(2)

    with col3:
        st.metric("预算总额",MONTHLY_BUDGET)

    with col4:
        st.metric("剩余预算",budget_left)

    if total_expense > MONTHLY_BUDGET:

        st.error("⚠ 已超过预算")

    elif total_expense > MONTHLY_BUDGET*0.8:

        st.warning("⚠ 已使用80%预算")

    # AI分析

    st.subheader("AI消费分析")

    if total_expense>0:

        top_category = expense.groupby(
            "category"
        )["amount"].sum().idxmax()

        avg_daily = total_expense / date.today().day

        st.write("本月消费最多类别:",top_category)

        st.write("平均每日消费:",round(avg_daily,2))

        if avg_daily>100:

            st.write("消费水平:较高")

        elif avg_daily>50:

            st.write("消费水平:中等")

        else:

            st.write("消费水平:较低")
