import numpy as np
import pandas as pd
import pyodbc
from transform import clean_dataframe, clean_inventory_data
from validation import validate_data_sources

# Cấu hình kết nối
SERVER_NAME = "LAPTOP-FES0O464"
DATABASE_NAME = "EcommerceLogistics"
EXCEL_PATH = "01_data/raw/data1.xlsx"

conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    r"Trusted_Connection=yes;"
)


def run_etl():
  conn = pyodbc.connect(conn_str)
  cursor = conn.cursor()

  try:
    print("1. Đang đọc dữ liệu từ Excel...")
    df_sku = pd.read_excel(EXCEL_PATH, sheet_name="SKU Masterdata")
    df_vendor = pd.read_excel(EXCEL_PATH, sheet_name="VendorMasterdata")
    df_inv = pd.read_excel(EXCEL_PATH, sheet_name="Inventory data")

    # Gọi module validation kiểm tra dữ liệu
    validate_data_sources(df_sku, df_inv)

    # Gọi module transform làm sạch dữ liệu
    df_sku = clean_dataframe(df_sku)
    df_vendor = clean_dataframe(df_vendor)
    df_inv = clean_inventory_data(df_inv)

    # 2. Nạp Staging SKU
    cursor.execute("TRUNCATE TABLE stg_SKUMasterdata;")
    sku_data = [
        tuple(
            val.item()
            if isinstance(val, np.generic)
            else (None if pd.isna(val) else val)
            for val in row
        )
        for row in df_sku.iloc[:, :7].itertuples(index=False, name=None)
    ]
    if sku_data:
      cursor.executemany(
          """
                INSERT INTO stg_SKUMasterdata ([Sku Code], [Sku Name], [SKU Short Name], [Primary Vendor], [Brand], [Sale Price], [Base Cost])
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
          sku_data,
      )

    # 3. Nạp Staging Vendor
    cursor.execute("TRUNCATE TABLE stg_VendorMasterdata;")
    vendor_col = (
        "Vendor Name"
        if "Vendor Name" in df_vendor.columns
        else df_vendor.columns[0]
    )
    vendor_data = [
        (val,) for val in df_vendor[vendor_col].dropna().unique() if pd.notna(val)
    ]
    if vendor_data:
      cursor.executemany(
          "INSERT INTO stg_VendorMasterdata ([Vendor]) VALUES (?)", vendor_data
      )

    # 4. Nạp Staging Inventory
    cursor.execute("TRUNCATE TABLE stg_InventoryData;")
    inv_data = [
        tuple(
            val.item()
            if isinstance(val, np.generic)
            else (None if pd.isna(val) else val)
            for val in row
        )
        for row in df_inv.iloc[:, :16].itertuples(index=False, name=None)
    ]
    if inv_data:
      cursor.executemany(
          """
                INSERT INTO stg_InventoryData (
                    [Sku_name], [Sku_code], [shop_account], [Tiki], [Lazada], [Shopee], 
                    [TikTok], [Sendo], [Tiki demand per...], [Lazada demand per...], 
                    [Shopee demand per...], [TikTok demand per...], [Sendo demand per...], 
                    [DOITarget_(days)], [Vendor], [Brand]
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
          inv_data,
      )

    # 5. Chuyển dữ liệu từ Staging sang Data Warehouse (Star Schema)
    print("Đang chuyển dữ liệu sang Data Warehouse (Dim & Fact)...")
    etl_sql = """
            TRUNCATE TABLE Dim_SKU;
            INSERT INTO Dim_SKU (Sku_Code, Sku_Name, SKU_Short_Name, Primary_Vendor, Brand, Sale_Price, Base_Cost)
            SELECT [Sku Code], MAX([Sku Name]), MAX([SKU Short Name]), MAX([Primary Vendor]), MAX([Brand]), 
                   TRY_CAST(MAX([Sale Price]) AS FLOAT), TRY_CAST(MAX([Base Cost]) AS FLOAT)
            FROM stg_SKUMasterdata WHERE [Sku Code] IS NOT NULL GROUP BY [Sku Code];

            TRUNCATE TABLE Dim_Vendor;
            INSERT INTO Dim_Vendor (Vendor_Name)
            SELECT DISTINCT [Vendor] FROM stg_VendorMasterdata WHERE [Vendor] IS NOT NULL;

            TRUNCATE TABLE Fact_Inventory;
            INSERT INTO Fact_Inventory (
                SKU_Code, Shop_Account, Tiki, Lazada, Shopee, TikTok, Sendo,
                Tiki_Demand_Per_Month, Lazada_Demand_Per_Month, Shopee_Demand_Per_Month,
                TikTok_Demand_Per_Month, Sendo_Demand_Per_Month, DOI_Target_Days, Vendor, Brand
            )
            SELECT [Sku_code], [shop_account], 
                   TRY_CAST([Tiki] AS FLOAT), TRY_CAST([Lazada] AS FLOAT), TRY_CAST([Shopee] AS FLOAT), 
                   TRY_CAST([TikTok] AS FLOAT), TRY_CAST([Sendo] AS FLOAT), 
                   TRY_CAST([Tiki demand per...] AS FLOAT), TRY_CAST([Lazada demand per...] AS FLOAT), 
                   TRY_CAST([Shopee demand per...] AS FLOAT), TRY_CAST([TikTok demand per...] AS FLOAT), 
                   TRY_CAST([Sendo demand per...] AS FLOAT), TRY_CAST([DOITarget_(days)] AS FLOAT), 
                   [Vendor], [Brand]
            FROM stg_InventoryData WHERE [Sku_code] IS NOT NULL;
        """
    cursor.execute(etl_sql)
    conn.commit()
    print("ETL Pipeline chạy hoàn tất và nạp Data Warehouse thành công!")

  except Exception as e:
    conn.rollback()
    print("Lỗi ETL:", e)
    raise
  finally:
    cursor.close()
    conn.close()


if __name__ == "__main__":
  run_etl()