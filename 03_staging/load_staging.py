
import numpy as np
import pandas as pd
import pyodbc

# 1. DATABASE CONNECTION

SERVER_NAME = "LAPTOP-FES0O464"
DATABASE_NAME = "EcommerceLogistics"
EXCEL_PATH = "D:/KDL/data1.xlsx"

conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    r"Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


# 2. CLEAN DATA


def clean_value(value):
  # Convert missing values to None
  if pd.isna(value):
    return None

  # Convert NumPy values to Python values
  if isinstance(value, np.generic):
    return value.item()

  return value


def clean_dataframe(df):
  # Remove completely empty rows
  df = df.dropna(how="all")

  # Convert missing values
  df = df.astype(object).where(pd.notna(df), None)

  return df


# 3. READ EXCEL FILE
try:
  df_sku = pd.read_excel(EXCEL_PATH, sheet_name="SKU Masterdata")

  df_vendor = pd.read_excel(EXCEL_PATH, sheet_name="VendorMasterdata")

  df_inv = pd.read_excel(EXCEL_PATH, sheet_name="Inventory data")

  # Clean data
  df_sku = clean_dataframe(df_sku)
  df_vendor = clean_dataframe(df_vendor)
  df_inv = clean_dataframe(df_inv)

  # Check column count
  if df_sku.shape[1] < 7:
    raise ValueError("SKU Masterdata must contain at least 7 columns.")

  if df_inv.shape[1] < 15:
    raise ValueError("Inventory data must contain at least 15 columns.")

  # 4. LOAD SKU STAGING TABLE

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

  # 5. LOAD VENDOR STAGING TABLE

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

  # 6. LOAD INVENTORY STAGING TABLE
  cursor.execute("TRUNCATE TABLE stg_InventoryData;")

  inventory_data = [
      tuple(clean_value(value) for value in row)
      for row in df_inv.iloc[:, :15].itertuples(index=False, name=None)
  ]

  if inventory_data:
    cursor.executemany(
        """
            INSERT INTO stg_InventoryData (
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
                ?, ?, ?, ?, ?
            )
            """,
        inventory_data,
    )

  # 7. ETL: STAGING -> DIMENSION & FACT

  etl_query = """
        -- Load Dimension SKU (Loại bỏ các mã SKU trùng lặp bằng GROUP BY)
        TRUNCATE TABLE Dim_SKU;

        INSERT INTO Dim_SKU (
            Sku_Code,
            Sku_Name,
            SKU_Short_Name,
            Primary_Vendor,
            Brand,
            Sale_Price,
            Base_Cost
        )
        SELECT 
            [Sku Code],
            MAX([Sku Name]) AS [Sku Name],
            MAX([SKU Short Name]) AS [SKU Short Name],
            MAX([Primary Vendor]) AS [Primary Vendor],
            MAX([Brand]) AS [Brand],
            MAX([Sale Price]) AS [Sale Price],
            MAX([Base Cost]) AS [Base Cost]
        FROM stg_SKUMasterdata
        WHERE [Sku Code] IS NOT NULL
        GROUP BY [Sku Code];


        -- Load Dimension Vendor
        TRUNCATE TABLE Dim_Vendor;

        INSERT INTO Dim_Vendor (
            Vendor_Name
        )
        SELECT DISTINCT
            [Vendor]
        FROM stg_VendorMasterdata
        WHERE [Vendor] IS NOT NULL;


        -- Load Fact Inventory
        TRUNCATE TABLE Fact_Inventory;

        INSERT INTO Fact_Inventory (
            SKU_Code,
            Shop_Account,
            Tiki,
            Lazada,
            Shopee,
            TikTok,
            Sendo,
            Tiki_Demand_Per_Month,
            Lazada_Demand_Per_Month,
            Shopee_Demand_Per_Month,
            TikTok_Demand_Per_Month,
            Sendo_Demand_Per_Month,
            DOI_Target_Days,
            Vendor,
            Brand
        )
        SELECT 
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
        FROM stg_InventoryData
        WHERE [Sku_code] IS NOT NULL;
    """

  cursor.execute(etl_query)

  # 8. COMMIT TRANSACTION

  conn.commit()

except Exception as e:
  conn.rollback()
  raise

finally:
  cursor.close()
  conn.close()
SERVER_NAME = "LAPTOP-FES0O464"
DATABASE_NAME = "EcommerceLogistics"
EXCEL_PATH = "D:/KDL/data1.xlsx"

conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    r"Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
