import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import altair as alt
import os

from helper.helper_data import *
from babel.numbers import format_currency
from mpl_toolkits.basemap import Basemap

sns.set(style='dark')
st.set_page_config(page_title = "E-Commerce Dashboard")

# Load cleaned data
all_df = pd.read_csv("main_data.csv")
late_delivery_geo_df = pd.read_csv("../data/late_delivery_geo.csv")

datetime_columns = ["shipping_limit_date","order_purchase_timestamp",
                    "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", 
                    "order_estimated_delivery_date"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

# Membuat sidebar
with st.sidebar:
    st.subheader('Input Start Date and End Date')
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Memfilter semua dataframe berdasarkan rentang tanggal
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# Menyiapkan berbagai dataframe
monthly_orders_df = create_monthly_orders_df(main_df)
most_used_payment_method_df = create_most_used_payment_df(main_df)
most_purchased_products_df = create_most_purchased_products_df(main_df)
most_purchased_product_categories_df = create_most_purchased_categories_df(main_df)
most_revenue_categories_df = create_most_revenue_categories_df(main_df)
rating_distribution_df = create_rating_distribution_df(main_df)
show_wordcloud = create_wordcloud(main_df)
count_by_status = create_late_delivery_rating_distribution_df(main_df)
hist_between_order_time = show_hist_between_order_time(main_df)
top_5_customer_cities_df = create_top_customer_cities_df(main_df)
top_5_seller_cities_df = create_top_seller_cities_df(main_df)
daily_sales_df = create_daily_sales_df(main_df)
hourly_sales_df = create_hourly_sales_df(main_df)
segment_counts, segment_percentages = create_customer_segmentation_df(main_df)


# Ploting number of monthly orders
st.header('Brazil E-Commerce Dashboard')
st.subheader('Monthly Orders')

col1, col2 = st.columns(2)
with col1:
    total_orders = monthly_orders_df["order_count"].sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(monthly_orders_df["revenue"].sum(), "BRL", locale='pt_BR')
    st.metric("Total Revenue", value=total_revenue)

with st.container():
   # Buat chart dengan Altair yang memiliki mark line dan mark point
    chart = alt.Chart(monthly_orders_df).mark_line().encode(
        x=alt.X('order_approved_at', title='Bulan'),
        y=alt.Y('order_count:Q', title='Jumlah Pesanan')
    ) + alt.Chart(monthly_orders_df).mark_circle().encode(
        x=alt.X('order_approved_at', title='Bulan'),
        y=alt.Y('order_count:Q', title='Jumlah Pesanan')
    )
    st.altair_chart(chart, use_container_width=True)
# End of plotting number of monthly orders

# Ploting the distribution of payment methods
st.subheader('Most Used Payment Methods')

with st.container():
    st.altair_chart(
       alt.Chart(most_used_payment_method_df).mark_bar().encode(
            x=alt.X('payment_type:N', title="Metode Pembayaran"),
            y=alt.Y('count:Q', title="Jumlah")
        ).properties(
            width=800,
            height=400
        ),
        use_container_width=True
    )
# End of ploting the distribution of payment methods

# Ploting the most purchased products
st.subheader('Most Purchased Products')

with st.container():
    st.altair_chart(
       alt.Chart(most_purchased_products_df).mark_bar().encode(
            x=alt.X('product_category_name_english:N', title="Produk"),
            y=alt.Y('order_count:Q', title="Jumlah")
        ).properties(
            width=800,
            height=400
        ),
        use_container_width=True
    )
# End of ploting the most purchased products

# Ploting the most purchased products categories
st.subheader('Most Purchased Products Categories')

with st.container():
    st.altair_chart(
       alt.Chart(most_purchased_product_categories_df.nlargest(5, "order_count")).mark_bar().encode(
            x=alt.X('product_category_name_english:N', title="Kategori Produk"),
            y=alt.Y('order_count:Q', title="Jumlah")
        ).properties(
            width=800,
            height=400
        ),
        use_container_width=True
    )
# End of ploting the most purchased products categories

# Ploting the most revenue product categories
st.subheader('Most Revenue Products Categories')

with st.container():
    st.altair_chart(
       alt.Chart(most_revenue_categories_df.nlargest(5, "total_revenue")).mark_bar().encode(
            x=alt.X('product_category_name_english:N', title="Produk"),
            y=alt.Y('total_revenue:Q', title="Jumlah Pendapatan")
        ).properties(
            width=800,
            height=400
        ),
        use_container_width=True
    )
# End of ploting the most revenue product categories

# Ploting the rating distribution
st.subheader('Rating Distribution Of All Products')

with st.container():
    st.altair_chart(
       alt.Chart(rating_distribution_df).mark_bar().encode(
            x=alt.X('review_score:N', title="Rating"),
            y=alt.Y('rating_count:Q', title="Jumlah")
        ).properties(
            width=800,
            height=400
        ),
        use_container_width=True
    )
# End of ploting the most revenue product categories

# Ploting the rating distribution
st.subheader('Show Wordcloud Of Products Rated Below 4')

with st.container():
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.imshow(show_wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(fig)
# End of ploting the the rating distribution

# Ploting the rating distribution of late delivered products
st.subheader('Show Rating Distribution Of Late Delivered Products')

with st.container():
    fig, ax = plt.subplots(figsize=(12, 6))
    plt.pie(count_by_status, labels=["Rating Below 4", "Rating Above 3"], autopct='%1.1f%%', startangle=140)
    plt.title("Store Rating Distribution", fontsize=24)
    plt.legend(title="Rating Status", labels=['Rating Below 4', 'Rating Above 3'])
    st.pyplot(fig)
# End of ploting the rating distribution of late delivered products

# Ploting the Comparison of Estimated Delivery Time with Actual Delivery Time
st.subheader('Show Comparison of Estimated Delivery Time with Actual Delivery Time')

with st.container():
    st.pyplot(hist_between_order_time)
# End of ploting the Comparison of Estimated Delivery Time with Actual Delivery Time

# Ploting the areas where many deliveries experience delays
st.subheader('Show Areas Where Many Deliveries Experience Delays')

with st.container():
    lat = late_delivery_geo_df['geolocation_lat']
    lon = late_delivery_geo_df['geolocation_lng']

    fig, ax = plt.subplots(figsize=(12, 6))
    m = Basemap(llcrnrlat=-55.401805,llcrnrlon=-92.269176,urcrnrlat=13.884615,urcrnrlon=-27.581676)
    m.bluemarble()
    m.drawmapboundary(fill_color='#46bcec')
    m.fillcontinents(color='#f2f2f2',lake_color='#46bcec')
    m.drawcoastlines()
    m.drawcountries()
    m.scatter(lon, lat,zorder=10,alpha=0.5,color='tomato')
    st.pyplot(fig)
# End of plotting the areas where many deliveries experience delays

# Ploting the top customer cities
st.subheader('Top Customer Cities')

with st.container():
    st.altair_chart(
       alt.Chart(top_5_customer_cities_df.sort_values(by = "count", ascending = False)).mark_bar().encode(
            x=alt.X('customer_city:N', title="Nama Kota"),
            y=alt.Y('count:Q', title="Jumlah")
        ).properties(
            width=800,
            height=400
        ),
        use_container_width=True
    )
# End of ploting the top customer cities

# Ploting the top seller cities
st.subheader('Top Seller Cities')

with st.container():
    st.altair_chart(
       alt.Chart(top_5_seller_cities_df.sort_values(by = "count", ascending = False)).mark_bar().encode(
            x=alt.X('seller_city:N', title="Nama Kota"),
            y=alt.Y('count:Q', title="Jumlah")
        ).properties(
            width=800,
            height=400
        ),
        use_container_width=True
    )
# End of ploting the top seller cities

# Ploting the time When Most Sales Occur
st.subheader('The Day When The Most Sales Occur')

with st.container():
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.set(style="whitegrid")
    sns.barplot(x='order_purchase_timestamp', y='order_id', data=daily_sales_df, color='b')
    plt.title('Grafik Jumlah Pesanan per Hari', fontsize=16)
    plt.xlabel('Hari', fontsize=12)
    plt.ylabel('Jumlah Pesanan', fontsize=12)
    st.pyplot(fig)
# End of ploting the the time When Most Sales Occur

# Ploting the time When Most Sales Occur
st.subheader('The Hour When The Most Sales Occur')

with st.container():
    # Buat chart dengan Altair yang memiliki mark line dan mark point
    chart = alt.Chart(hourly_sales_df).mark_line().encode(
    x=alt.X('Jam', title='Jam'),
    y=alt.Y('Jumlah Pesanan:Q', title='Jumlah Pesanan')
    ) + alt.Chart(hourly_sales_df).mark_point().encode(
        x=alt.X('Jam', title='Jam'),
        y=alt.Y('Jumlah Pesanan:Q', title='Jumlah Pesanan')
    )

    st.altair_chart(chart, use_container_width=True)
# End of ploting the time When Most Sales Occur

# Ploting the customer segmentation
st.subheader('Customer Segmentation Based From RFM')

with st.container():
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=segment_counts.index, y=segment_counts, palette="Set3")
    plt.xlabel('Segment')
    plt.ylabel('Jumlah Pelanggan')
    plt.title('Distribusi Pelanggan per Segmen')

    # Menambahkan persentase di atas setiap bar
    for i in range(len(segment_counts)):
        plt.text(i, segment_counts[i] + 5, f"{segment_percentages[i]:.2f}%", ha='center', va='bottom')

    st.pyplot(fig)
# End of ploting the customer segmentation

st.caption('Copyright © Muhammad Sya\'bani Falif 2023')