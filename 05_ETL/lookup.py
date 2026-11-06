import pandas as pd

# Chuẩn hóa khóa dùng để đối chiếu
def normalize_key(value):
    if pd.isna(value):
        return None
    return str(value).strip().casefold()

def perform_lookup(df_fact, conn):
    # 1. Lấy dữ liệu từ các bảng Dimension trong SQL Server
    df_product = pd.read_sql("SELECT ProductKey, SkuCode, BaseCost FROM Dim_Product", conn)
    df_channel = pd.read_sql("SELECT ChannelKey, ChannelName FROM Dim_Channel", conn)
    df_shop = pd.read_sql("SELECT ShopKey, ShopAccount FROM Dim_Shop", conn)

    # 2. Chuẩn hóa khóa nghiệp vụ trước khi tạo mapping
    df_product["LookupKey"] = df_product["SkuCode"].apply(normalize_key)
    df_channel["LookupKey"] = df_channel["ChannelName"].apply(normalize_key)
    df_shop["LookupKey"] = df_shop["ShopAccount"].apply(normalize_key)

    # 3. Kiểm tra khóa nghiệp vụ bị trùng trong Dimension
    for name, df in [
        ("Dim_Product", df_product),
        ("Dim_Channel", df_channel),
        ("Dim_Shop", df_shop)
    ]:
        duplicated = df["LookupKey"].duplicated(keep=False)
        if duplicated.any():
            raise ValueError(f"{name} có khóa nghiệp vụ bị trùng. " "Cần kiểm tra trước khi thực hiện Lookup.")

    # 4. Tạo mapping từ khóa nghiệp vụ sang khóa thay thế
    product_map = df_product.set_index("LookupKey")["ProductKey"].to_dict()
    channel_map = df_channel.set_index("LookupKey")["ChannelKey"].to_dict()
    shop_map = df_shop.set_index("LookupKey")["ShopKey"].to_dict()
    base_cost_map = df_product.set_index("LookupKey")["BaseCost"].to_dict()

    fact_rows = []
    lookup_errors = []

    # 5. Thực hiện Lookup cho từng bản ghi Fact
    for index, row in df_fact.iterrows():
        sku = normalize_key(row["Sku_code"])
        channel = normalize_key(row["ChannelName"])
        shop = normalize_key(row["shop_account"])
        p_key = product_map.get(sku)
        c_key = channel_map.get(channel)
        s_key = shop_map.get(shop)
        base_cost = base_cost_map.get(sku)
        # Kiểm tra các khóa và BaseCost
        missing_fields = []
        if p_key is None:
            missing_fields.append("ProductKey")
        if c_key is None:
            missing_fields.append("ChannelKey")
        if s_key is None:
            missing_fields.append("ShopKey")
        if pd.isna(base_cost):
            missing_fields.append("BaseCost")
        if missing_fields:
            lookup_errors.append({
                "RowIndex": index,
                "Sku_code": row["Sku_code"],
                "ChannelName": row["ChannelName"],
                "shop_account": row["shop_account"],
                "Error": ", ".join(missing_fields)
            })
            continue

        # 6. Lấy các chỉ tiêu tồn kho
        stock = row["StockQuantity"]
        demand = row["MonthlyDemand"]
        doi = row["DOITarget (days)"]
        # Không tự chuyển dữ liệu thiếu thành 0
        if pd.isna(stock) or pd.isna(demand) or pd.isna(doi):
            lookup_errors.append({
                "RowIndex": index,
                "Sku_code": row["Sku_code"],
                "ChannelName": row["ChannelName"],
                "shop_account": row["shop_account"],
                "Error": "Thiếu dữ liệu StockQuantity, MonthlyDemand hoặc DOITarget"
            })
            continue

        # 7. Tính giá trị tồn kho
        inv_value = stock * base_cost

        # 8. Lưu bản ghi đã Lookup thành công
        fact_rows.append((
            p_key,
            c_key,
            s_key,
            stock,
            demand,
            doi,
            inv_value
        ))

    # 9. Thông báo kết quả Lookup
    print(f"Số bản ghi Lookup thành công: {len(fact_rows)}")
    print(f"Số bản ghi Lookup lỗi: {len(lookup_errors)}")
    return fact_rows, lookup_errors
