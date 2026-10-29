
import math
import re
import unicodedata

import numpy as np
import pandas as pd
import pyodbc

from transform import clean_dataframe, clean_inventory_data
from validation import validate_data_sources


# ============================================================
# 1. CẤU HÌNH KẾT NỐI SQL SERVER
# ============================================================

SERVER_NAME = "LAPTOP-FES0O464"
DATABASE_NAME = "EcommerceLogistics"
EXCEL_PATH = "01_data/raw/data1.xlsx"

conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    r"Trusted_Connection=yes;"
)


# ============================================================
# 2. CHUẨN HÓA TÊN CỘT
# ============================================================

def normalize_name(value):
    value = str(value).strip().casefold()
    value = unicodedata.normalize("NFKD", value)

    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )

    value = value.replace("_", " ")
    value = re.sub(r"[^a-z0-9]+", " ", value)

    return re.sub(r"\s+", " ", value).strip()


def normalize_inventory_columns(df):
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]

    aliases = {
        "Sku_name": [
            "Sku_name", "SKU Name", "Sku Name",
            "SKU_Name", "Product Name"
        ],
        "Sku_code": [
            "Sku_code", "SKU Code", "Sku Code",
            "SKU_Code", "Sku"
        ],
        "shop_account": [
            "shop_account", "SHOP_ACCOUNT",
            "Shop Account", "Shop_Account"
        ],
        "Tiki": ["Tiki"],
        "Lazada": ["Lazada"],
        "Shopee": ["Shopee"],
        "TikTok": ["TikTok", "Tik Tok"],
        "Sendo": ["Sendo"],
        "Tiki demand per...": [
            "Tiki demand per...",
            "Tiki demand",
            "Tiki Demand Per Day",
            "Tiki Demand Per Month"
        ],
        "Lazada demand per...": [
            "Lazada demand per...",
            "Lazada demand",
            "Lazada Demand Per Day",
            "Lazada Demand Per Month"
        ],
        "Shopee demand per...": [
            "Shopee demand per...",
            "Shopee demand",
            "Shopee Demand Per Day",
            "Shopee Demand Per Month"
        ],
        "TikTok demand per...": [
            "TikTok demand per...",
            "TikTok demand",
            "Tik Tok Demand",
            "TikTok Demand Per Day",
            "TikTok Demand Per Month"
        ],
        "Sendo demand per...": [
            "Sendo demand per...",
            "Sendo demand",
            "Sendo Demand Per Day",
            "Sendo Demand Per Month"
        ],
        "DOITarget_(days)": [
            "DOITarget_(days)",
            "DOI Target (days)",
            "DOI Target",
            "DOITarget",
            "DOI Target Days"
        ],
        "Vendor": ["Vendor", "VENDOR"],
        "Brand": ["Brand", "BRAND"],
    }

    actual_columns = {}

    for col in df.columns:
        key = normalize_name(col)
        actual_columns.setdefault(key, col)

    rename_map = {}
    used_columns = set()

    for target, candidates in aliases.items():
        for candidate in candidates:
            actual = actual_columns.get(
                normalize_name(candidate)
            )

            if (
                actual is not None
                and actual not in used_columns
            ):
                rename_map[actual] = target
                used_columns.add(actual)
                break

    df = df.rename(columns=rename_map)

    # Tìm các cột demand có tên gần giống nhau.
    for col in list(df.columns):
        normalized = normalize_name(col)
        target = None

        for channel in [
            "Tiki", "Lazada", "Shopee", "TikTok", "Sendo"
        ]:
            channel_normalized = normalize_name(channel)

            if (
                normalized.startswith(channel_normalized + " ")
                and "demand" in normalized
            ):
                target = f"{channel} demand per..."
                break

        if target and target not in df.columns:
            df = df.rename(columns={col: target})

    # Chuẩn hóa cột DOI Target.
    for col in list(df.columns):
        normalized = normalize_name(col)

        if (
            "doi" in normalized
            and (
                "target" in normalized
                or "day" in normalized
            )
            and "DOITarget_(days)" not in df.columns
        ):
            df = df.rename(
                columns={col: "DOITarget_(days)"}
            )
            break

    return df


# ============================================================
# 3. XỬ LÝ GIÁ TRỊ NULL VÀ KIỂU DỮ LIỆU
# ============================================================

def safe_value(value):
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


def safe_text(value):
    value = safe_value(value)

    if value is None:
        return None

    return str(value).strip()


def safe_float(value, default=0.0):
    value = safe_value(value)

    if value is None:
        return default

    try:
        number = float(value)

        if not math.isfinite(number):
            return default

        return number

    except (ValueError, TypeError, OverflowError):
        return default


def dataframe_to_tuples(df):
    return [
        tuple(safe_value(value) for value in row)
        for row in df.itertuples(
            index=False,
            name=None
        )
    ]


# ============================================================
# 4. INSERT BATCH VÀ KIỂM TRA DÒNG LỖI
# ============================================================

def insert_batch(cursor, sql, data, table_name):
    if not data:
        print(f"Bảng {table_name} không có dữ liệu.")
        return

    try:
        cursor.executemany(sql, data)

        print(
            f"Đã nạp {len(data):,} dòng vào {table_name}."
        )

    except pyodbc.Error as batch_error:
        # Rollback batch lỗi trước khi kiểm tra từng dòng.
        cursor.connection.rollback()

        print(f"Lỗi INSERT tại bảng {table_name}.")
        print("Đang kiểm tra từng dòng dữ liệu...")

        for index, record in enumerate(data):
            try:
                cursor.execute(sql, record)

            except pyodbc.Error as row_error:
                cursor.connection.rollback()

                print(f"Bảng lỗi: {table_name}")
                print(f"Vị trí dòng trong batch: {index}")
                print(f"Dữ liệu lỗi: {record!r}")

                print(
                    "Kiểu dữ liệu:",
                    [
                        type(value).__name__
                        for value in record
                    ]
                )

                print(f"Chi tiết lỗi: {row_error}")
                print(f"Lỗi batch ban đầu: {batch_error}")

                raise

        # Nếu từng dòng chạy riêng đều được nhưng batch lỗi,
        # không tiếp tục với giao dịch đã bị rollback.
        cursor.connection.rollback()

        raise RuntimeError(
            f"INSERT batch thất bại tại {table_name}. "
            "Hãy kiểm tra kiểu dữ liệu SQL Server."
        ) from batch_error


# ============================================================
# 5. CHẠY ETL
# ============================================================

def run_etl():
    conn = None
    cursor = None

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        print("1. Đang đọc dữ liệu từ Excel...")

        df_sku = pd.read_excel(
            EXCEL_PATH,
            sheet_name="SKU Masterdata"
        )

        df_vendor = pd.read_excel(
            EXCEL_PATH,
            sheet_name="VendorMasterdata"
        )

        df_inv = pd.read_excel(
            EXCEL_PATH,
            sheet_name="Inventory data"
        )

        print("2. Đang kiểm tra dữ liệu...")

        validate_data_sources(df_sku, df_inv)

        print("3. Đang làm sạch dữ liệu...")

        df_sku = clean_dataframe(df_sku)
        df_vendor = clean_dataframe(df_vendor)
        df_inv = clean_inventory_data(df_inv)

        df_inv = normalize_inventory_columns(df_inv)

        # ----------------------------------------------------
        # NẠP DỮ LIỆU STAGING
        # ----------------------------------------------------

        print("4. Đang nạp dữ liệu vào Staging...")

        # SKU Masterdata
        sku_columns = [
            "Sku Code",
            "Sku Name",
            "SKU Short Name",
            "Primary Vendor",
            "Brand",
            "Sale Price",
            "Base Cost"
        ]

        sku_data = dataframe_to_tuples(
            df_sku[sku_columns]
        )

        cursor.execute(
            "DELETE FROM stg_SKUMasterdata;"
        )

        sku_sql = """
            INSERT INTO stg_SKUMasterdata (
                [Sku Code],
                [Sku Name],
                [SKU Short Name],
                [Primary Vendor],
                [Brand],
                [Sale Price],
                [Base Cost]
            )
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """

        insert_batch(
            cursor,
            sku_sql,
            sku_data,
            "stg_SKUMasterdata"
        )

        # Vendor Masterdata
        vendor_data = []

        for _, row in df_vendor.iterrows():
            v_acc = safe_text(
                row.get("SHOP_ACCOUNT")
            )

            if "VENDOR" in df_vendor.columns:
                v_code_raw = row.get("VENDOR")
            else:
                v_code_raw = (
                    row.iloc[1]
                    if len(row) > 1
                    else None
                )

            vendor_data.append((
                v_acc,
                safe_text(v_code_raw),
                safe_text(row.get("BRAND")),
                safe_text(row.get("Vendor Name")),
                safe_text(row.get("Shipping Adress")),
                safe_float(
                    row.get("Payment Terms (per week)"),
                    default=0.0
                )
            ))

        cursor.execute(
            "DELETE FROM stg_VendorMasterdata;"
        )

        vendor_sql = """
            INSERT INTO stg_VendorMasterdata (
                [SHOP_ACCOUNT],
                [VENDOR],
                [BRAND],
                [Vendor Name],
                [Shipping Adress],
                [Payment Terms (per week)]
            )
            VALUES (?, ?, ?, ?, ?, ?);
        """

        insert_batch(
            cursor,
            vendor_sql,
            vendor_data,
            "stg_VendorMasterdata"
        )

        # Inventory data
        inventory_columns = [
            "Sku_name",
            "Sku_code",
            "shop_account",
            "Tiki",
            "Lazada",
            "Shopee",
            "TikTok",
            "Sendo",
            "Tiki demand per...",
            "Lazada demand per...",
            "Shopee demand per...",
            "TikTok demand per...",
            "Sendo demand per...",
            "DOITarget_(days)",
            "Vendor",
            "Brand"
        ]

        inv_data = dataframe_to_tuples(
            df_inv[inventory_columns]
        )

        cursor.execute(
            "DELETE FROM stg_InventoryData;"
        )

        inventory_sql = """
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
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?
            );
        """

        insert_batch(
            cursor,
            inventory_sql,
            inv_data,
            "stg_InventoryData"
        )

        # ----------------------------------------------------
        # 6. NẠP DỮ LIỆU DATA WAREHOUSE
        # ----------------------------------------------------

        print("5. Đang nạp dữ liệu vào Data Warehouse...")

        # Xóa bảng Fact trước Dimension để tránh lỗi FOREIGN KEY.
        # Không sử dụng NOCHECK vì cần giữ nguyên tính toàn vẹn
        # tham chiếu của dữ liệu.

        cursor.execute(
            "DELETE FROM Fact_Inventory_Snapshot;"
        )

        cursor.execute(
            "DELETE FROM Dim_Product;"
        )

        cursor.execute(
            "DELETE FROM Dim_Supplier;"
        )

        cursor.execute(
            "DELETE FROM Dim_Channel;"
        )

        cursor.execute(
            "DELETE FROM Dim_Shop;"
        )

        # ----------------------------------------------------
        # INSERT CÁC DIMENSION VÀ FACT
        # ----------------------------------------------------

        etl_sql = """
            -- 1. Nạp bảng Dim_Product
            INSERT INTO Dim_Product (
                SkuCode,
                SkuName,
                SKUShortName,
                Brand,
                SalePrice,
                BaseCost,
                PrimaryVendor
            )
            SELECT
                [Sku Code],
                MAX([Sku Name]),
                MAX([SKU Short Name]),
                MAX([Brand]),
                TRY_CAST(
                    MAX([Sale Price]) AS DECIMAL(18,2)
                ),
                TRY_CAST(
                    MAX([Base Cost]) AS DECIMAL(18,2)
                ),
                MAX([Primary Vendor])
            FROM stg_SKUMasterdata
            WHERE [Sku Code] IS NOT NULL
            GROUP BY [Sku Code];


            -- 2. Nạp bảng Dim_Supplier
            INSERT INTO Dim_Supplier (
                VendorCode,
                VendorName,
                ShippingAddress,
                PaymentTermsPerWeek
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


            -- 3. Nạp danh sách kênh bán hàng
            INSERT INTO Dim_Channel (
                ChannelName
            )
            VALUES
                ('Tiki'),
                ('Lazada'),
                ('Shopee'),
                ('TikTok'),
                ('Sendo');


            -- 4. Nạp danh sách tài khoản cửa hàng
            INSERT INTO Dim_Shop (
                ShopAccount
            )
            SELECT DISTINCT
                [shop_account]
            FROM stg_InventoryData
            WHERE [shop_account] IS NOT NULL;


            -- 5. Nạp tồn kho Tiki
            INSERT INTO Fact_Inventory_Snapshot (
                ProductKey,
                ChannelKey,
                ShopKey,
                StockQuantity,
                MonthlyDemand,
                DOITargetDays,
                InventoryValue
            )
            SELECT
                p.ProductKey,
                c.ChannelKey,
                s.ShopKey,
                TRY_CAST(
                    i.[Tiki] AS DECIMAL(18,2)
                ),
                TRY_CAST(
                    i.[Tiki demand per...]
                    AS DECIMAL(18,4)
                ),
                TRY_CAST(
                    i.[DOITarget_(days)]
                    AS DECIMAL(10,2)
                ),
                TRY_CAST(
                    i.[Tiki] AS DECIMAL(18,2)
                ) * ISNULL(p.BaseCost, 0)
            FROM stg_InventoryData AS i
            INNER JOIN Dim_Product AS p
                ON i.[Sku_code] = p.SkuCode
            INNER JOIN Dim_Channel AS c
                ON c.ChannelName = 'Tiki'
            LEFT JOIN Dim_Shop AS s
                ON i.[shop_account] = s.ShopAccount
            WHERE i.[Sku_code] IS NOT NULL;


            -- 6. Nạp tồn kho Lazada
            INSERT INTO Fact_Inventory_Snapshot (
                ProductKey,
                ChannelKey,
                ShopKey,
                StockQuantity,
                MonthlyDemand,
                DOITargetDays,
                InventoryValue
            )
            SELECT
                p.ProductKey,
                c.ChannelKey,
                s.ShopKey,
                TRY_CAST(
                    i.[Lazada] AS DECIMAL(18,2)
                ),
                TRY_CAST(
                    i.[Lazada demand per...]
                    AS DECIMAL(18,4)
                ),
                TRY_CAST(
                    i.[DOITarget_(days)]
                    AS DECIMAL(10,2)
                ),
                TRY_CAST(
                    i.[Lazada] AS DECIMAL(18,2)
                ) * ISNULL(p.BaseCost, 0)
            FROM stg_InventoryData AS i
            INNER JOIN Dim_Product AS p
                ON i.[Sku_code] = p.SkuCode
            INNER JOIN Dim_Channel AS c
                ON c.ChannelName = 'Lazada'
            LEFT JOIN Dim_Shop AS s
                ON i.[shop_account] = s.ShopAccount
            WHERE i.[Sku_code] IS NOT NULL;


            -- 7. Nạp tồn kho Shopee
            INSERT INTO Fact_Inventory_Snapshot (
                ProductKey,
                ChannelKey,
                ShopKey,
                StockQuantity,
                MonthlyDemand,
                DOITargetDays,
                InventoryValue
            )
            SELECT
                p.ProductKey,
                c.ChannelKey,
                s.ShopKey,
                TRY_CAST(
                    i.[Shopee] AS DECIMAL(18,2)
                ),
                TRY_CAST(
                    i.[Shopee demand per...]
                    AS DECIMAL(18,4)
                ),
                TRY_CAST(
                    i.[DOITarget_(days)]
                    AS DECIMAL(10,2)
                ),
                TRY_CAST(
                    i.[Shopee] AS DECIMAL(18,2)
                ) * ISNULL(p.BaseCost, 0)
            FROM stg_InventoryData AS i
            INNER JOIN Dim_Product AS p
                ON i.[Sku_code] = p.SkuCode
            INNER JOIN Dim_Channel AS c
                ON c.ChannelName = 'Shopee'
            LEFT JOIN Dim_Shop AS s
                ON i.[shop_account] = s.ShopAccount
            WHERE i.[Sku_code] IS NOT NULL;


            -- 8. Nạp tồn kho TikTok
            INSERT INTO Fact_Inventory_Snapshot (
                ProductKey,
                ChannelKey,
                ShopKey,
                StockQuantity,
                MonthlyDemand,
                DOITargetDays,
                InventoryValue
            )
            SELECT
                p.ProductKey,
                c.ChannelKey,
                s.ShopKey,
                TRY_CAST(
                    i.[TikTok] AS DECIMAL(18,2)
                ),
                TRY_CAST(
                    i.[TikTok demand per...]
                    AS DECIMAL(18,4)
                ),
                TRY_CAST(
                    i.[DOITarget_(days)]
                    AS DECIMAL(10,2)
                ),
                TRY_CAST(
                    i.[TikTok] AS DECIMAL(18,2)
                ) * ISNULL(p.BaseCost, 0)
            FROM stg_InventoryData AS i
            INNER JOIN Dim_Product AS p
                ON i.[Sku_code] = p.SkuCode
            INNER JOIN Dim_Channel AS c
                ON c.ChannelName = 'TikTok'
            LEFT JOIN Dim_Shop AS s
                ON i.[shop_account] = s.ShopAccount
            WHERE i.[Sku_code] IS NOT NULL;


            -- 9. Nạp tồn kho Sendo
            INSERT INTO Fact_Inventory_Snapshot (
                ProductKey,
                ChannelKey,
                ShopKey,
                StockQuantity,
                MonthlyDemand,
                DOITargetDays,
                InventoryValue
            )
            SELECT
                p.ProductKey,
                c.ChannelKey,
                s.ShopKey,
                TRY_CAST(
                    i.[Sendo] AS DECIMAL(18,2)
                ),
                TRY_CAST(
                    i.[Sendo demand per...]
                    AS DECIMAL(18,4)
                ),
                TRY_CAST(
                    i.[DOITarget_(days)]
                    AS DECIMAL(10,2)
                ),
                TRY_CAST(
                    i.[Sendo] AS DECIMAL(18,2)
                ) * ISNULL(p.BaseCost, 0)
            FROM stg_InventoryData AS i
            INNER JOIN Dim_Product AS p
                ON i.[Sku_code] = p.SkuCode
            INNER JOIN Dim_Channel AS c
                ON c.ChannelName = 'Sendo'
            LEFT JOIN Dim_Shop AS s
                ON i.[shop_account] = s.ShopAccount
            WHERE i.[Sku_code] IS NOT NULL;
        """

        cursor.execute(etl_sql)

        # Chỉ commit sau khi toàn bộ quá trình thành công.
        conn.commit()

        print("\nETL Pipeline chạy hoàn tất!")
        print(f"Số dòng SKU: {len(sku_data):,}")
        print(f"Số dòng Vendor: {len(vendor_data):,}")
        print(f"Số dòng Inventory: {len(inv_data):,}")
        print(
            "Đã nạp dữ liệu vào Data Warehouse thành công."
        )

    except Exception as e:
        if conn is not None:
            conn.rollback()

        print("\nLỗi ETL:", repr(e))
        print("Đã rollback giao dịch.")

        raise

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None:
            conn.close()


if __name__ == "__main__":
    run_etl()

