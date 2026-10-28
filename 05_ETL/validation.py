import pandas as pd


def validate_data_sources(df_sku, df_inv):
  # Kiểm tra số cột tối thiểu của SKU Masterdata
  if df_sku.shape[1] < 7:
    raise ValueError(
        f"Lỗi Validation: SKU Masterdata phải có ít nhất 7 cột (hiện có"
        f" {df_sku.shape[1]} cột)."
    )

  # Kiểm tra số cột tối thiểu của Inventory Data
  if df_inv.shape[1] < 16:
    raise ValueError(
        f"Lỗi Validation: Inventory data phải có ít nhất 16 cột (hiện có"
        f" {df_inv.shape[1]} cột)."
    )

  print("Kiểm tra cấu trúc dữ liệu (Validation) thành công!")
  return True