import numpy as np
import pandas as pd
import pyodbc

# 1. Kết nối SQL Server
SERVER_NAME = "LAPTOP-FES0O464"
DATABASE_NAME = "EcommerceLogistics"
EXCEL_PATH = "01_data/raw/data1.xlsx"

conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    r"Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


# 2. Xử lý dữ liệu
def clean_value(value):
  if pd.isna(value):
    return None
  if isinstance(value, np.generic):
    return value.item()
  return value


def clean_dataframe(df):
  df = df.dropna(how="all")
  df = df.astype(object).where(pd.notna(df), None)
  return df


# 3. Đọc dữ liệu từ Excel
try:
  df_sku = pd.read_excel(EXCEL_PATH, sheet_name="SKU Masterdata")
  df_vendor = pd.read_excel(EXCEL_PATH, sheet_name="VendorMasterdata")
  df_inv = pd.read_excel(EXCEL_PATH, sheet_name="Inventory data")

  # Làm sạch dữ liệu
  df_sku = clean_dataframe(df_sku)
  df_vendor = clean_dataframe(df_vendor)
  df_inv = clean_dataframe(df_inv)

  # Kiểm tra số lượng cột
  if df_sku.shape[1] < 7:
    raise ValueError("SKU Masterdata phải có ít nhất 7 cột.")

  if df_inv.shape[1] < 16:
    raise ValueError(
        f"Inventory data phải có ít nhất 16 cột (hiện tại có {df_inv.shape[1]} cột)."
    )

  print("Đọc dữ liệu Excel thành công!")

  # 4. Nạp dữ liệu SKU vào bảng trung gian (Khớp chuẩn tên cột có khoảng trắng)
  cursor.execute("TRUNCATE TABLE stg_SKUMasterdata;")

  sku_data = [
      tuple(clean_value(value) for value in row)
      for row in df_sku.iloc[:, :7].itertuples(index=False, name=None)
  ]

  if sku_data:
    cursor.executemany(
        """
            INSERT INTO stg_SKUMasterdata (
                [Sku Code],
                [Sku Name],
                [SKU Short Name],
                [Primary Vendor],
                [Brand],
                [Sale Price],
                [Base Cost]
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
        sku_data,
    )

  print("Nạp dữ liệu stg_SKUMasterdata thành công!")

  # 5. Nạp dữ liệu nhà cung cấp vào bảng trung gian
  cursor.execute("TRUNCATE TABLE stg_VendorMasterdata;")

  vendor_data = [
      (clean_value(row[0]),)
      for row in df_vendor.itertuples(index=False, name=None)
      if row[0] is not None
  ]

  if vendor_data:
    cursor.executemany(
        """
            INSERT INTO stg_VendorMasterdata ([Vendor])
            VALUES (?)
            """,
        vendor_data,
    )

  print("Nạp dữ liệu stg_VendorMasterdata thành công!")

  # 6. Nạp dữ liệu tồn kho vào bảng trung gian
  cursor.execute("TRUNCATE TABLE stg_InventoryData;")

  inventory_data = [
      tuple(clean_value(value) for value in row)
      for row in df_inv.iloc[:, :16].itertuples(index=False, name=None)
  ]

  if inventory_data:
    cursor.executemany(
        """
            INSERT INTO stg_InventoryData (
                [Sku_name],
                [Sku_code],
                [shop_account],
                [Tiki],
                [Lazada],
                [Shopee],
                [TikTok],
                [Sendo],
                [Tiki demand per...],
                [Lazada demand per...],
                [Shopee demand per...],
                [TikTok demand per...],
                [Sendo demand per...],
                [DOITarget_(days)],
                [Vendor],
                [Brand]
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?
            )
            """,
        inventory_data,
    )

  print("Nạp dữ liệu stg_InventoryData thành công!")

  # 7. Chuyển dữ liệu từ bảng trung gian sang Dim_Product đúng chuẩn thiết kế
  etl_query = """
        -- Nạp dữ liệu vào bảng Dim_Product (đồng bộ với cấu trúc thiết kế chiều sản phẩm)
        TRUNCATE TABLE Dim_Product;

        INSERT INTO Dim_Product (
            SkuCode,
            SkuName,
            SKUShortName,
            PrimaryVendor,
            Brand,
            SalePrice,
            BaseCost
        )
        SELECT
            [Sku Code],
            MAX([Sku Name]) AS SkuName,
            MAX([SKU Short Name]) AS SKUShortName,
            MAX([Primary Vendor]) AS PrimaryVendor,
            MAX([Brand]) AS Brand,
            MAX([Sale Price]) AS SalePrice,
            MAX([Base Cost]) AS BaseCost
        FROM stg_SKUMasterdata
        WHERE [Sku Code] IS NOT NULL
        GROUP BY [Sku Code];


        -- Nạp dữ liệu vào bảng Dim_Supplier (tương ứng Dim_Vendor)
        TRUNCATE TABLE Dim_Supplier;

        INSERT INTO Dim_Supplier (
            VendorName
        )
        SELECT DISTINCT
            [Vendor]
        FROM stg_VendorMasterdata
        WHERE [Vendor] IS NOT NULL;
    """

  cursor.execute(etl_query)

  # 8. Lưu dữ liệu vào SQL Server
  conn.commit()
  print("ETL hoàn thành thành công!")

except Exception as e:
  conn.rollback()
  print("ETL thất bại!")
  print("Lỗi:", e)
  raise

finally:
  cursor.close()
  conn.close()
  print("Đã đóng kết nối SQL Server.")
