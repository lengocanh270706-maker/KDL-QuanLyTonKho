import pyodbc

# Cấu hình kết nối
SERVER_NAME = "LAPTOP-FES0O464"  # Sửa theo server trên máy mng
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
        print("Đang nạp dữ liệu vào các bảng Dimension theo mô hình Chương 2...")

        # 1. Tắt tạm thời khóa ngoại từ bảng Fact trỏ tới Dim để tránh lỗi khi xóa/nạp
        cursor.execute("ALTER TABLE Fact_Inventory_Snapshot NOCHECK CONSTRAINT ALL;")

        # 2. Xóa dữ liệu các bảng Dim theo thứ tự (hoặc dùng DELETE)
        cursor.execute("DELETE FROM Dim_Product;")
        cursor.execute("DELETE FROM Dim_Supplier;")
        cursor.execute("DELETE FROM Dim_Channel;")
        cursor.execute("DELETE FROM Dim_Shop;")

        # 3. Nạp Dim_Product
        cursor.execute("""
            INSERT INTO Dim_Product (
                SkuCode, SkuName, SKUShortName,
                Brand, SalePrice, BaseCost, PrimaryVendor
            )
            SELECT
                [Sku Code],
                MAX([Sku Name]),
                MAX([SKU Short Name]),
                MAX([Brand]),
                TRY_CAST(MAX([Sale Price]) AS DECIMAL(18,2)),
                TRY_CAST(MAX([Base Cost]) AS DECIMAL(18,2)),
                MAX([Primary Vendor])
            FROM stg_SKUMasterdata
            WHERE [Sku Code] IS NOT NULL
            GROUP BY [Sku Code];
        """)

        # 4. Nạp Dim_Supplier
        cursor.execute("""
            INSERT INTO Dim_Supplier (
                VendorCode, VendorName,
                ShippingAddress, PaymentTermsPerWeek
            )
            SELECT
                [VENDOR],
                MAX([Vendor Name]),
                MAX([Shipping Adress]),
                TRY_CAST(
                    MAX([Payment Terms (per week)])
                    AS DECIMAL(10,2)
                )
            FROM stg_VendorMasterdata
            WHERE [VENDOR] IS NOT NULL
            GROUP BY [VENDOR];
        """)

        # 5. Nạp Dim_Channel
        cursor.execute("""
            INSERT INTO Dim_Channel (ChannelName)
            VALUES
                ('Tiki'),
                ('Lazada'),
                ('Shopee'),
                ('TikTok'),
                ('Sendo');
        """)

        # 6. Nạp Dim_Shop
        cursor.execute("""
            INSERT INTO Dim_Shop (ShopAccount)
            SELECT DISTINCT [shop_account]
            FROM stg_InventoryData
            WHERE [shop_account] IS NOT NULL;
        """)

        # 7. Bật lại khóa ngoại sau khi nạp xong
        cursor.execute("ALTER TABLE Fact_Inventory_Snapshot CHECK CONSTRAINT ALL;")

        conn.commit()
        print("Nạp toàn bộ các bảng Dimension theo mô hình Chương 2 thành công rực rỡ!")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi nạp Dimension Chương 2: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    load_dimensions()
