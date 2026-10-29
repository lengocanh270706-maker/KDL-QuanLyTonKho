import pandas as pd

def validate_data_sources(df_sku, df_inv):
    """Hàm kiểm tra sơ bộ nguồn dữ liệu đầu vào trước khi nạp"""
    print("Đang thực hiện kiểm tra chất lượng dữ liệu (Validation)...")
    
    if df_sku is None or df_inv is None:
        raise ValueError("Dữ liệu nguồn bị trống (None)!")
        
    print(f"Kiểm tra thành công: SKU Masterdata có {len(df_sku)} dòng, Inventory data có {len(df_inv)} dòng.")
    return True