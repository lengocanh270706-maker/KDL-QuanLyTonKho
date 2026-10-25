import pandas as pd
import pyodbc

SERVER_NAME = "localhost" #đổi tên server mấy ní nha
DATABASE_NAME = "EcommerceLogistics"
EXCEL_PATH = "D:/KDL/data1.xlsx" #đổi tên đường dẫn trên máy 

conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    r"Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

try:
  # 1. Nạp SKU Masterdata
  df_sku = pd.read_excel(EXCEL_PATH, sheet_name="SKU Masterdata")
  cursor.execute("TRUNCATE TABLE stg_SKUMasterdata;")
  for _, row in df_sku.iterrows():
    cursor.execute(
        """
            INSERT INTO stg_SKUMasterdata ([Sku Code], [Sku Name], [SKU Short Name], [Primary Vendor], [Brand], [Sale Price], [Base Cost])
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        tuple(row),
    )

  # 2. Nạp Vendor Masterdata
  df_vendor = pd.read_excel(EXCEL_PATH, sheet_name="VendorMasterdata")
  cursor.execute("TRUNCATE TABLE stg_VendorMasterdata;")
  for _, row in df_vendor.iterrows():
    cursor.execute(
        "INSERT INTO stg_VendorMasterdata ([Vendor]) VALUES (?)", tuple(row)
    )

  # 3. Nạp Inventory Data
  df_inv = pd.read_excel(EXCEL_PATH, sheet_name="Inventory data")
  cursor.execute("TRUNCATE TABLE stg_InventoryData;")
  for _, row in df_inv.iterrows():
    cursor.execute(
        """
            INSERT INTO stg_InventoryData (
                [Sku_code], [shop_account], [Tiki], [Lazada], [Shopee], [TikTok], [Sendo],
                [Tiki demand per...], [Lazada demand per...], [Shopee demand per...],
                [TikTok demand per...], [Sendo demand per...], [DOITarget_(days)], [Vendor], [Brand]
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        tuple(row),
    )

  conn.commit()

  # 4. ETL chạy thẳng vào Star Schema
  etl_query = """
    -- 1. Dim_SKU
    TRUNCATE TABLE Dim_SKU;
    INSERT INTO Dim_SKU (Sku_Code, Sku_Name, SKU_Short_Name, Primary_Vendor, Brand, Sale_Price, Base_Cost)
    SELECT [Sku Code], [Sku Name], [SKU Short Name], [Primary Vendor], [Brand], [Sale Price], [Base Cost]
    FROM stg_SKUMasterdata;

    -- 2. Dim_Vendor
    TRUNCATE TABLE Dim_Vendor;
    INSERT INTO Dim_Vendor (Vendor_Name)
    SELECT DISTINCT [Vendor]
    FROM stg_VendorMasterdata
    WHERE [Vendor] IS NOT NULL;

    -- 3. Fact_Inventory
    TRUNCATE TABLE Fact_Inventory;
    INSERT INTO Fact_Inventory (
        SKU_Code, Shop_Account, Tiki, Lazada, Shopee, TikTok, Sendo,
        Tiki_Demand_Per_Month, Lazada_Demand_Per_Month, Shopee_Demand_Per_Month,
        TikTok_Demand_Per_Month, Sendo_Demand_Per_Month, DOI_Target_Days, Vendor, Brand
    )
    SELECT 
        [Sku_code], [shop_account], [Tiki], [Lazada], [Shopee], [TikTok], [Sendo],
        [Tiki demand per...], [Lazada demand per...], [Shopee demand per...],
        [TikTok demand per...], [Sendo demand per...], [DOITarget_(days)], [Vendor], [Brand]
    FROM stg_InventoryData;
    """
  cursor.execute(etl_query)
  conn.commit()

except Exception as e:
  conn.rollback()

finally:
  cursor.close()
  conn.close()
