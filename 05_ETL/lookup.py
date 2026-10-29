import pandas as pd

def perform_lookup(df_fact, conn):
    # Lấy mapping từ SQL Server
    product_map = pd.read_sql("SELECT ProductKey, SkuCode FROM Dim_Product", conn).set_index('SkuCode')['ProductKey'].to_dict()
    channel_map = pd.read_sql("SELECT ChannelKey, ChannelName FROM Dim_Channel", conn).set_index('ChannelName')['ChannelKey'].to_dict()
    shop_map = pd.read_sql("SELECT ShopKey, ShopAccount FROM Dim_Shop", conn).set_index('ShopAccount')['ShopKey'].to_dict()
    base_cost_map = pd.read_sql("SELECT SkuCode, BaseCost FROM Dim_Product", conn).set_index('SkuCode')['BaseCost'].to_dict()

    fact_rows = []
    lookup_errors = 0

    for _, row in df_fact.iterrows():
        sku = row['Sku_code']
        shop = row['shop_account']
        channel = row['ChannelName']
        
        p_key = product_map.get(sku)
        c_key = channel_map.get(channel)
        s_key = shop_map.get(shop, None)
        
        if p_key and c_key:
            stock = row['StockQuantity']
            demand = row['MonthlyDemand']
            doi = row['DOITarget (days)']
            base_cost = base_cost_map.get(sku, 0)
            inv_value = stock * base_cost # Tính giá trị tồn kho theo Chương 2
            
            fact_rows.append((p_key, c_key, s_key, stock, demand, doi, inv_value))
        else:
            lookup_errors += 1

    if lookup_errors > 0:
        print(f"Cảnh báo Lookup: Có {lookup_errors} bản ghi không khớp khóa ngoại bị cô lập.")
        
    return fact_rows