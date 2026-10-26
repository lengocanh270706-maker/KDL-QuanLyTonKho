import pyodbc

# Cấu hình kết nối
SERVER_NAME = "LAPTOP-FES0O464" #sửa theo server trên máy mng
DATABASE_NAME = "EcommerceLogistics"

conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    r"Trusted_Connection=yes;"
)


def load_dimensions():
  conn = pyodbc.connect(conn_str)
  cursor = conn.cursor()
  try:
    print("Đang nạp dữ liệu vào các bảng Dimension...")

    # Nạp Dim_SKU (Sử dụng GROUP BY để loại bỏ các mã SKU trùng lặp)
    cursor.execute("""
            TRUNCATE TABLE Dim_SKU;

            INSERT INTO Dim_SKU (
                Sku_Code, Sku_Name, SKU_Short_Name, Primary_Vendor, Brand, Sale_Price, Base_Cost
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
        """)

    # Nạp Dim_Vendor (Sử dụng DISTINCT để lấy danh sách nhà cung cấp duy nhất)
    cursor.execute("""
            TRUNCATE TABLE Dim_Vendor;

            INSERT INTO Dim_Vendor (Vendor_Name)
            SELECT DISTINCT [Vendor]
            FROM stg_VendorMasterdata
            WHERE [Vendor] IS NOT NULL;
        """)

    conn.commit()
    print("Nạp dữ liệu Dim_SKU và Dim_Vendor thành công!")

  except Exception as e:
    conn.rollback()
    print(f"Lỗi khi nạp Dimension: {e}")
    raise
  finally:
    cursor.close()
    conn.close()


if __name__ == "__main__":
  load_dimensions()
