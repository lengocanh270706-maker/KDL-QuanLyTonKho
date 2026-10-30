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


def load_fact():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    try:
        print("Đang nạp dữ liệu vào bảng Fact_Inventory_Snapshot theo mô hình Chương 2...")

        # 1. Tắt tạm thời khóa ngoại để tránh xung đột khi truncate bảng Fact
        cursor.execute("ALTER TABLE Fact_Inventory_Snapshot NOCHECK CONSTRAINT ALL;")

        # 2. Xóa sạch dữ liệu cũ của bảng Fact
        cursor.execute("TRUNCATE TABLE Fact_Inventory_Snapshot;")

        # 3. Nạp dữ liệu Unpivot theo từng kênh (Tiki, Lazada, Shopee, TikTok, Sendo)
        fact_sql = """
            -- Tiki
            INSERT INTO Fact_Inventory_Snapshot (
                ProductKey, ChannelKey, ShopKey,
                StockQuantity, MonthlyDemand,
                DOITargetDays, InventoryValue
            )
            SELECT
                p.ProductKey,
                c.ChannelKey,
                s.ShopKey,
                TRY_CAST(i.[Tiki] AS DECIMAL(18,2)),
                TRY_CAST(i.[Tiki demand per...] AS DECIMAL(18,4)),
                TRY_CAST(i.[DOITarget_(days)] AS DECIMAL(10,2)),
                TRY_CAST(i.[Tiki] AS DECIMAL(18,2)) * ISNULL(p.BaseCost, 0)
            FROM stg_InventoryData i
            JOIN Dim_Product p ON i.[Sku_code] = p.SkuCode
            JOIN Dim_Channel c ON c.ChannelName = 'Tiki'
            LEFT JOIN Dim_Shop s ON i.[shop_account] = s.ShopAccount
            WHERE i.[Sku_code] IS NOT NULL;

            -- Lazada
            INSERT INTO Fact_Inventory_Snapshot (
                ProductKey, ChannelKey, ShopKey,
                StockQuantity, MonthlyDemand,
                DOITargetDays, InventoryValue
            )
            SELECT
                p.ProductKey,
                c.ChannelKey,
                s.ShopKey,
                TRY_CAST(i.[Lazada] AS DECIMAL(18,2)),
                TRY_CAST(i.[Lazada demand per...] AS DECIMAL(18,4)),
                TRY_CAST(i.[DOITarget_(days)] AS DECIMAL(10,2)),
                TRY_CAST(i.[Lazada] AS DECIMAL(18,2)) * ISNULL(p.BaseCost, 0)
            FROM stg_InventoryData i
            JOIN Dim_Product p ON i.[Sku_code] = p.SkuCode
            JOIN Dim_Channel c ON c.ChannelName = 'Lazada'
            LEFT JOIN Dim_Shop s ON i.[shop_account] = s.ShopAccount
            WHERE i.[Sku_code] IS NOT NULL;

            -- Shopee
            INSERT INTO Fact_Inventory_Snapshot (
                ProductKey, ChannelKey, ShopKey,
                StockQuantity, MonthlyDemand,
                DOITargetDays, InventoryValue
            )
            SELECT
                p.ProductKey,
                c.ChannelKey,
                s.ShopKey,
                TRY_CAST(i.[Shopee] AS DECIMAL(18,2)),
                TRY_CAST(i.[Shopee demand per...] AS DECIMAL(18,4)),
                TRY_CAST(i.[DOITarget_(days)] AS DECIMAL(10,2)),
                TRY_CAST(i.[Shopee] AS DECIMAL(18,2)) * ISNULL(p.BaseCost, 0)
            FROM stg_InventoryData i
            JOIN Dim_Product p ON i.[Sku_code] = p.SkuCode
            JOIN Dim_Channel c ON c.ChannelName = 'Shopee'
            LEFT JOIN Dim_Shop s ON i.[shop_account] = s.ShopAccount
            WHERE i.[Sku_code] IS NOT NULL;

            -- TikTok
            INSERT INTO Fact_Inventory_Snapshot (
                ProductKey, ChannelKey, ShopKey,
                StockQuantity, MonthlyDemand,
                DOITargetDays, InventoryValue
            )
            SELECT
                p.ProductKey,
                c.ChannelKey,
                s.ShopKey,
                TRY_CAST(i.[TikTok] AS DECIMAL(18,2)),
                TRY_CAST(i.[TikTok demand per...] AS DECIMAL(18,4)),
                TRY_CAST(i.[DOITarget_(days)] AS DECIMAL(10,2)),
                TRY_CAST(i.[TikTok] AS DECIMAL(18,2)) * ISNULL(p.BaseCost, 0)
            FROM stg_InventoryData i
            JOIN Dim_Product p ON i.[Sku_code] = p.SkuCode
            JOIN Dim_Channel c ON c.ChannelName = 'TikTok'
            LEFT JOIN Dim_Shop s ON i.[shop_account] = s.ShopAccount
            WHERE i.[Sku_code] IS NOT NULL;

            -- Sendo
            INSERT INTO Fact_Inventory_Snapshot (
                ProductKey, ChannelKey, ShopKey,
                StockQuantity, MonthlyDemand,
                DOITargetDays, InventoryValue
            )
            SELECT
                p.ProductKey,
                c.ChannelKey,
                s.ShopKey,
                TRY_CAST(i.[Sendo] AS DECIMAL(18,2)),
                TRY_CAST(i.[Sendo demand per...] AS DECIMAL(18,4)),
                TRY_CAST(i.[DOITarget_(days)] AS DECIMAL(10,2)),
                TRY_CAST(i.[Sendo] AS DECIMAL(18,2)) * ISNULL(p.BaseCost, 0)
            FROM stg_InventoryData i
            JOIN Dim_Product p ON i.[Sku_code] = p.SkuCode
            JOIN Dim_Channel c ON c.ChannelName = 'Sendo'
            LEFT JOIN Dim_Shop s ON i.[shop_account] = s.ShopAccount
            WHERE i.[Sku_code] IS NOT NULL;
        """

        cursor.execute(fact_sql)

        # 4. Bật lại khóa ngoại sau khi nạp xong
        cursor.execute("ALTER TABLE Fact_Inventory_Snapshot CHECK CONSTRAINT ALL;")

        conn.commit()
        print("Nạp dữ liệu Fact_Inventory_Snapshot thành công!")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Lỗi khi nạp Fact: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    load_fact()
