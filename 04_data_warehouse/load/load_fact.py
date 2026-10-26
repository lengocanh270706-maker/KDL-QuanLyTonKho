import pyodbc

# Cấu hình kết nối
SERVER_NAME = "LAPTOP-FES0O464"
DATABASE_NAME = "EcommerceLogistics"

conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    r"Trusted_Connection=yes;"
)


def load_fact():
  conn = pyodbc.connect(conn_str)
  cursor = conn.cursor()
  try:
    print("Đang nạp dữ liệu vào bảng Fact_Inventory...")

    # Nạp Fact_Inventory từ bảng Staging Inventory
    cursor.execute("""
            TRUNCATE TABLE Fact_Inventory;

            INSERT INTO Fact_Inventory (
                SKU_Code, Shop_Account, Tiki, Lazada, Shopee, TikTok, Sendo,
                Tiki_Demand_Per_Month, Lazada_Demand_Per_Month, Shopee_Demand_Per_Month,
                TikTok_Demand_Per_Month, Sendo_Demand_Per_Month, DOI_Target_Days, Vendor, Brand
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
        """)

    conn.commit()
    print("Nạp dữ liệu Fact_Inventory thành công!")

  except Exception as e:
    conn.rollback()
    print(f"Lỗi khi nạp Fact: {e}")
    raise
  finally:
    cursor.close()
    conn.close()


if __name__ == "__main__":
  load_fact()
