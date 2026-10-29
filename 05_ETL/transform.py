import pandas as pd

def clean_dataframe(df):
    """Hàm làm sạch chung cho các bảng SKU và Vendor"""
    df_cleaned = df.copy()
    # Loại bỏ khoảng trắng thừa cho các cột kiểu chuỗi
    for col in df_cleaned.select_dtypes(include=['object']).columns:
        df_cleaned[col] = df_cleaned[col].astype(str).str.strip()
    return df_cleaned

def clean_inventory_data(df):
    """Hàm làm sạch riêng cho bảng Inventory data"""
    df_cleaned = df.copy()
    if 'Sku_code' in df_cleaned.columns:
        df_cleaned['Sku_code'] = df_cleaned['Sku_code'].astype(str).str.strip()
    if 'shop_account' in df_cleaned.columns:
        df_cleaned['shop_account'] = df_cleaned['shop_account'].astype(str).str.strip()
    return df_cleaned