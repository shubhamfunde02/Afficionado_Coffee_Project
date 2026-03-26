import pandas as pd
import streamlit as st
import plotly.express as px


# PAGE CONFIG

st.set_page_config(page_title="Afficionado Coffee Dashboard", layout="wide")


# LOAD DATA

data = pd.read_csv("Afficionado Coffee Roasters.xlsx - Transactions.csv")


# DATA PREPROCESSING

data['revenue'] = data['transaction_qty'] * data['unit_price']

data['transaction_time'] = pd.to_datetime(data['transaction_time'])
data['hour'] = data['transaction_time'].dt.hour
data['weekday'] = data['transaction_time'].dt.day_name()
data['month'] = data['transaction_time'].dt.month_name()


# SIDEBAR FILTERS

st.sidebar.title("🔎 Filters")

store = st.sidebar.selectbox("Select Store Location", data['store_location'].unique())
category = st.sidebar.selectbox("Select Category", data['product_category'].unique())
product_type = st.sidebar.selectbox("Select Product Type", data['product_type'].unique())

top_n = st.sidebar.slider("Top N Products", 5, 20, 10)

view_type = st.sidebar.radio("Trend View", ["Hour", "Weekday", "Month"])

# FILTER DATA

filtered_data = data[
    (data['store_location'] == store) &
    (data['product_category'] == category) &
    (data['product_type'] == product_type)
]

# KPI CALCULATIONS

total_revenue = filtered_data['revenue'].sum()
total_qty = filtered_data['transaction_qty'].sum()
total_products = filtered_data['product_id'].nunique()

# PRODUCT LEVEL ANALYSIS

product_summary = filtered_data.groupby('product_id').agg({
    'transaction_qty': 'sum',
    'revenue': 'sum'
}).reset_index()

product_summary['revenue_pct'] = (product_summary['revenue'] / total_revenue) * 100
product_summary = product_summary.sort_values(by='revenue', ascending=False)


# CATEGORY ANALYSIS

category_summary = data.groupby('product_category')['revenue'].sum().reset_index()


# PARETO ANALYSIS (80/20)

pareto = product_summary.sort_values(by='revenue', ascending=False)
pareto['cum_revenue'] = pareto['revenue'].cumsum()
pareto['cum_pct'] = pareto['cum_revenue'] / pareto['revenue'].sum() * 100


# UI DESIGN (CSS)

st.markdown("""
<style>
body {background-color: #f4e1d2;}
[data-testid="stMetric"] {
    background-color: #e6c7a9;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# TITLE

st.title("☕ Afficionado Coffee Roasters Dashboard")


# KPI ROW

k1, k2, k3 = st.columns(3)

k1.metric("Total Revenue", f"${total_revenue:,.0f}")
k2.metric("Total Sales Volume", f"{total_qty:,}")
k3.metric("Total Products", total_products)


# ROW 2 - PRODUCT INSIGHTS

col1, col2 = st.columns(2)

# 🔹 Top Products by Revenue
with col1:
    st.subheader("🏆 Top Products by Revenue")

    top_products = product_summary.head(top_n)

    fig1 = px.bar(
        top_products,
        x='revenue',
        y='product_id',
        orientation='h',
        color='revenue',
        color_continuous_scale='Oranges'
    )
    fig1.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)

# 🔹 Category Revenue Share
with col2:
    st.subheader("📊 Category Revenue Contribution")

    fig2 = px.pie(
        category_summary,
        names='product_category',
        values='revenue',
        hole=0.6,
        color_discrete_sequence=px.colors.sequential.Reds
    )
    st.plotly_chart(fig2, use_container_width=True)

# ROW 3 - SCATTER + TREND

col3, col4 = st.columns(2)

# 🔹Popularity vs Revenue
with col3:
    st.subheader("📈 Popularity vs Revenue")

    fig3 = px.scatter(
        product_summary,
        x='transaction_qty',
        y='revenue',
        size='revenue',
        color='product_id',
        hover_name='product_id',
        title="Product Efficiency"
    )
    st.plotly_chart(fig3, use_container_width=True)

# 🔹 Time Trends
if view_type == "Hour":
    group_col = 'hour'
elif view_type == "Weekday":
    group_col = 'weekday'
else:
    group_col = 'month'

trend = filtered_data.groupby(group_col)['revenue'].sum().reset_index()

with col4:
    st.subheader(f"⏱ Sales Trend ({view_type})")

    fig4 = px.area(
        trend,
        x=group_col,
        y='revenue',
        color_discrete_sequence=['#C67C4E']
    )
    st.plotly_chart(fig4, use_container_width=True)


# ROW 4 - PARETO ANALYSIS

st.subheader("📉 Pareto Analysis (80/20 Rule)")

fig5 = px.line(
    pareto,
    x=pareto.index,
    y='cum_pct',
    title="Cumulative Revenue %",
)

fig5.add_hline(y=80, line_dash="dash", line_color="red")

st.plotly_chart(fig5, use_container_width=True)


# TABLE

st.subheader("📋 Product Performance Table")

st.dataframe(product_summary)