
import numpy as np
import pandas as pd
import pyodbc

# 1. Kết nối SQL Server
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


# 2. Xử lý dữ liệu
def clean_value(value):
    # Thay giá trị thiếu bằng None
    if pd.isna(value):
        return None

    # Chuyển kiểu NumPy sang kiểu Python
    if isinstance(value, np.generic):
        return value.item()

    return value


def clean_dataframe(df):
    # Xóa các dòng trống hoàn toàn
    df = df.dropna(how="all")

    # Chuẩn hóa giá trị thiếu
    df = df.astype(object).where(pd.notna(df), None)

    return df


# 3. Đọc dữ liệu từ Excel
try:
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

    # Làm sạch dữ liệu
    df_sku = clean_dataframe(df_sku)
    df_vendor = clean_dataframe(df_vendor)
    df_inv = clean_dataframe(df_inv)

    # Kiểm tra số lượng cột
    if df_sku.shape[1] < 7:
        raise ValueError(
            "SKU Masterdata phải có ít nhất 7 cột."
        )

    if df_inv.shape[1] < 15:
        raise ValueError(
            "Inventory data phải có ít nhất 15 cột."
        )

    print("Đọc dữ liệu Excel thành công!")


    # 4. Nạp dữ liệu SKU vào bảng trung gian
    cursor.execute("TRUNCATE TABLE stg_SKUMasterdata;")

    sku_data = [
        tuple(clean_value(value) for value in row)
        for row in df_sku.iloc[:, :7].itertuples(
            index=False,
            name=None
        )
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
            sku_data
        )

    print("Nạp dữ liệu SKU thành công!")


    # 5. Nạp dữ liệu nhà cung cấp vào bảng trung gian
    cursor.execute("TRUNCATE TABLE stg_VendorMasterdata;")

    vendor_data = [
        (clean_value(row[0]),)
        for row in df_vendor.itertuples(
            index=False,
            name=None
        )
        if row[0] is not None
    ]

    if vendor_data:
        cursor.executemany(
            """
            INSERT INTO stg_VendorMasterdata ([Vendor])
            VALUES (?)
            """,
            vendor_data
        )

    print("Nạp dữ liệu nhà cung cấp thành công!")


    # 6. Nạp dữ liệu tồn kho vào bảng trung gian
    cursor.execute("TRUNCATE TABLE stg_InventoryData;")

    inventory_data = [
        tuple(clean_value(value) for value in row)
        for row in df_inv.iloc[:, :15].itertuples(
            index=False,
            name=None
        )
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
            inventory_data
        )

    print("Nạp dữ liệu tồn kho thành công!")


    # 7. Chuyển dữ liệu từ bảng trung gian sang Dim và Fact
    etl_query = """

        -- Nạp dữ liệu vào bảng Dim_SKU
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


        -- Nạp dữ liệu vào bảng Dim_Vendor
        TRUNCATE TABLE Dim_Vendor;

        INSERT INTO Dim_Vendor (
            Vendor_Name
        )
        SELECT DISTINCT
            [Vendor]
        FROM stg_VendorMasterdata
        WHERE [Vendor] IS NOT NULL;


        -- Nạp dữ liệu vào bảng Fact_Inventory
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

    # 8. Lưu dữ liệu vào SQL Server
    conn.commit()

    print("ETL hoàn thành thành công!")

except Exception as e:

    # Hoàn tác nếu xảy ra lỗi
    conn.rollback()

    print("ETL thất bại!")
    print("Lỗi:", e)

    raise

finally:

    # Đóng kết nối cơ sở dữ liệu
    cursor.close()
    conn.close()

    print("Đã đóng kết nối SQL Server.")
