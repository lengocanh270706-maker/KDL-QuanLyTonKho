import numpy as np
import pandas as pd


def clean_dataframe(df):
  """Hàm làm sạch chung cho các DataFrame:

  - Xóa các dòng trống hoàn toàn (NaN all).
  - Cắt bỏ khoảng trắng thừa cho mọi cột kiểu chuỗi.
  - Chuyển các chuỗi 'nan', 'None', rỗng thành giá trị NA chuẩn.
  """
  df = df.dropna(how="all")

  for col in df.select_dtypes(include=["object"]).columns:
    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
        .replace(["nan", "None", ""], pd.NA)
    )

  return df


def clean_inventory_data(df_inv):
  """Hàm làm sạch chuyên biệt cho dữ liệu tồn kho (Inventory data):

  - Kế thừa hàm clean_dataframe.
  - Xử lý các cột số lượng/nhu cầu, bóc tách ký tự rác (dấu '#', khoảng trắng).
  - Điền giá trị mặc định cho shop_account, Brand và Vendor nếu bị thiếu.
  """
  df_inv = clean_dataframe(df_inv)

  # 1. Danh sách các cột số lượng, nhu cầu và chỉ số cần chuẩn hóa an toàn
  numeric_cols = [
      "Tiki",
      "Lazada",
      "Shopee",
      "TikTok",
      "Sendo",
      "Tiki demand per month",
      "Lazada demand per month",
      "Shopee demand per month",
      "TikTok demand per month",
      "Sendo demand per month",
      "DOITarget\n(days)",
  ]

  for col in numeric_cols:
    if col in df_inv.columns:
      # Chuyển sang chuỗi, loại bỏ ký tự '#' hoặc khoảng trắng thừa gây lỗi định dạng
      cleaned_series = (
          df_inv[col].astype(str).str.replace("#", "", regex=False).str.strip()
      )
      # Ép kiểu sang float, các ô không hợp lệ sẽ tự động chuyển thành NaN
      df_inv[col] = pd.to_numeric(cleaned_series, errors="coerce")

  # 2. Xử lý các cột định tính bị thiếu 
  if "shop_account" in df_inv.columns:
    df_inv["shop_account"] = (
        df_inv["shop_account"]
        .astype(str)
        .str.strip()
        .replace(["nan", "None", ""], "Chưa rõ Shop")
        .fillna("Chưa rõ Shop")
    )

  if "Brand" in df_inv.columns:
    df_inv["Brand"] = (
        df_inv["Brand"]
        .astype(str)
        .str.strip()
        .replace(["nan", "None", ""], "Chưa phân loại")
        .fillna("Chưa phân loại")
    )

  if "Vendor" in df_inv.columns:
    df_inv["Vendor"] = (
        df_inv["Vendor"]
        .astype(str)
        .str.strip()
        .replace(["nan", "None", ""], "Chưa xác định")
        .fillna("Chưa xác định")
    )

  return df_inv