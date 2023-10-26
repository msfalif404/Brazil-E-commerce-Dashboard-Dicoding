import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from wordcloud import WordCloud

def create_monthly_orders_df(all_df):
    monthly_orders_df = all_df.resample(rule = "M", on = "order_approved_at").agg({
    "order_id": "nunique",
    "payment_value": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return monthly_orders_df

def create_most_used_payment_df(all_df):
    most_used_payment_method_df = all_df.groupby(by = "payment_type")["order_id"].nunique().reset_index()
    most_used_payment_method_df.rename(columns = {
        "order_id": "count"
    }, inplace = True)

    return most_used_payment_method_df

def create_most_purchased_products_df(all_df):
    most_purchased_products_df = all_df.groupby(["product_id","product_category_name_english"])["order_id"].nunique().reset_index()
    most_purchased_products_df.rename(columns = {
        "order_id": "order_count"
    }, inplace = True)
    most_purchased_products_df = most_purchased_products_df.nlargest(6, "order_count")

    return most_purchased_products_df

def create_most_purchased_categories_df(all_df):
    most_purchased_product_categories_df = all_df.groupby(by = "product_category_name_english")["order_id"].nunique().reset_index()
    most_purchased_product_categories_df.rename(columns = {
        "order_id": "order_count"
    }, inplace = True)

    return most_purchased_product_categories_df

def create_most_revenue_categories_df(all_df):
    most_revenue_categories_df = all_df.groupby(by = "product_category_name_english", as_index = False).agg({
    "order_id": "nunique",
    "payment_value": "sum",
    })
    most_revenue_categories_df.rename(columns = {
        "order_id": "order_count",
        "payment_value": "total_revenue"
    }, inplace = True)

    return most_revenue_categories_df

def create_rating_distribution_df(all_df):
    rating_distribution_df = all_df.groupby(by = "review_score")["order_id"].nunique().reset_index()
    rating_distribution_df.rename(columns = {
        "order_id": "rating_count"
    }, inplace = True)

    return rating_distribution_df

def create_wordcloud(all_df):
    all_df["score_status"] = all_df["review_score"].apply(lambda x: 1 if x > 3 else -1)

    # Filter hanya data dengan review_score == 1 dan review_comment_title adalah string
    text = " ".join(all_df[(all_df['score_status'] == -1) & all_df['review_comment_title'].notna()]['review_comment_title'].astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)

    return wordcloud

def create_late_delivery_rating_distribution_df(all_df):
    late_delivery_orders_df = all_df[all_df["order_delivered_customer_date"] > all_df["order_estimated_delivery_date"]]
    count_by_status = late_delivery_orders_df['score_status'].value_counts()

    return count_by_status

def show_hist_between_order_time(all_df):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(all_df['order_delivered_customer_date'], kde=True, color='blue', label='Delivered Date')
    sns.histplot(all_df['order_estimated_delivery_date'], kde=True, color='green', label='Estimated Delivery Date')

    plt.title("Difference Between Estimated Delivery Date and Delivered Date")
    plt.legend()
    plt.ylabel(None)
    plt.xlabel(None)
    
    return fig

def create_top_customer_cities_df(all_df):
    top_5_customer_cities_df = all_df.groupby(by = "customer_city")["customer_id"].nunique().sort_values(ascending = False).nlargest(5).reset_index()
    top_5_customer_cities_df.rename(columns = {
        "customer_id": "count"
    }, inplace = True)

    return top_5_customer_cities_df

def create_top_seller_cities_df(all_df):
    top_5_seller_cities_df = all_df.groupby(by = "seller_city")["seller_id"].nunique().sort_values(ascending = False).nlargest(5).reset_index()
    top_5_seller_cities_df.rename(columns = {
        "seller_id": "count"
    }, inplace = True)

    return top_5_seller_cities_df

def create_daily_sales_df(all_df):
    daily_sales = all_df.groupby(all_df['order_purchase_timestamp'].dt.dayofweek)['order_id'].nunique()

    # Membuat dictionary untuk mengonversi indeks (0-6) ke hari (Senin-Minggu)
    day_mapping = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}

    # Mengonversi indeks menjadi nama hari
    daily_sales.index = daily_sales.index.map(day_mapping)
    daily_sales = daily_sales.reset_index()

    return daily_sales

def create_hourly_sales_df(all_df):
    hourly_sales = all_df.groupby(all_df['order_purchase_timestamp'].dt.hour)['order_id'].nunique()
    hourly_sales_df = pd.DataFrame({'Jam': hourly_sales.index, 'Jumlah Pesanan': hourly_sales.values})

    return hourly_sales_df

def create_customer_segmentation_df(all_df):
    max_date = all_df["order_purchase_timestamp"].max()

    rfm_df = all_df.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (max_date - x.max()).days,
        'order_id':'count',
        'payment_value':'sum'
    }).reset_index()

    rfm_df.columns =['customer_id','recency','frequency','monetary']

    #memberikan peringkat pada kolom frequency
    rfm_df['frequency'] = rfm_df['frequency'].rank(method='first', ascending=False)

    # Setiap kuartil dibagi menjadi 5 kelompok dengan penanda atau label yang sesuai.
    # Selanjutnya, kuartil-kuartil ini digunakan untuk membuat nilai RFM_Score, yang akan digunakan untuk segmentasi pelanggan.

    rfm_df['r_quartile'] = pd.qcut(rfm_df['recency'], 5, ['5','4','3','2','1'])
    rfm_df['f_quartile'] = pd.qcut(rfm_df['frequency'], 5, labels=['1', '2', '3', '4', '5'], duplicates='drop')
    rfm_df['m_quartile'] = pd.qcut(rfm_df['monetary'], 5, ['1','2','3','4','5'])
    rfm_df["RFM_Score"] = rfm_df["r_quartile"].astype(int) + rfm_df["f_quartile"].astype(int) + rfm_df["m_quartile"].astype(int)

    seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At Risk',
    r'[1-2]5': 'Can\'t Lose',
    r'3[1-2]': 'About to Sleep',
    r'33': 'Need Attention',
    r'[3-4][4-5]': 'Loyal Customers',
    r'41': 'Promising',
    r'51': 'New Customers',
    r'[4-5][2-3]': 'Potential Loyalists',
    r'5[4-5]': 'Champions'
}

    rfm_df['segment'] = rfm_df['r_quartile'].astype(str) + rfm_df['f_quartile'].astype(str)
    rfm_df['segment'] = rfm_df['segment'].replace(seg_map, regex=True)

    # Filter data berdasarkan nilai segmen yang diinginkan
    desired_segments = ['Loyal Customers', 'Promising', 'Potential Loyalists', 'Champions', 'Kecanduan']
    rfm_df = rfm_df[rfm_df['segment'].isin(desired_segments)]

    # Hitung jumlah observasi per segmen
    segment_counts = rfm_df['segment'].value_counts()

    # Hitung persentase
    segment_percentages = (segment_counts / segment_counts.sum()) * 100

    return (segment_counts, segment_percentages)