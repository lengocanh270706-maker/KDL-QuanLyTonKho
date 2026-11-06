import pandas as pd
import numpy as np
from pathlib import Path

# 1. CẤU HÌNH ĐƯỜNG DẪN VÀ TÊN SHEET
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR.parent / "01_data" / "raw" / "data1.xlsx"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "data1_cleaned.xlsx"
SHEETS = ["Inventory data", "SKU Masterdata", "VendorMasterdata"]

# Các cột số thường gặp trong dữ liệu tồn kho.
# Chỉ những cột thực sự tồn tại mới được chuyển đổi.
NUMERIC_COLUMNS = [
    "StockQuantity",
    "MonthlyDemand",
    "BaseCost",
    "TargetDaysStock",
    "InventoryValue",
    "Quantity",
    "UnitPrice",
    "TotalAmount"
]

# Chỉ điền 0 cho các cột này khi nhóm đã xác nhận:
# ô trống có nghĩa là chưa phát sinh dữ liệu.
# Nếu chưa xác nhận, để danh sách rỗng: ZERO_IF_NOT_GENERATED = []
ZERO_IF_NOT_GENERATED = ["StockQuantity", "MonthlyDemand"]

# Danh sách cột kiểm tra không được âm.
NON_NEGATIVE_COLUMNS = [
    "StockQuantity",
    "MonthlyDemand",
    "BaseCost",
    "TargetDaysStock",
    "Quantity",
    "UnitPrice",
    "TotalAmount"
]

# 2. KHỞI TẠO CÁC DANH SÁCH GHI NHẬN
errors = []
lookup_errors = []
quality = []
summary = []
# Lưu thống kê tổng quan sau tiền xử lý
# Lưu các ô có dữ liệu gốc nhưng chuyển đổi số thất bại.
# Mục đích: không nhầm lỗi chuyển đổi với NULL ban đầu
# khi xử lý các cột được phép điền 0.
invalid_numeric_cells = set()

# 3. CHUẨN HÓA DỮ LIỆU CHUỖI
def clean_text(df):
    """Chuẩn hóa tên cột và loại bỏ khoảng trắng thừa."""
    df = df.copy()
    # Chuẩn hóa tên cột
    df.columns = (df.columns.astype(str).str.strip().str.replace(r"\s+", " ", regex=True))
    # Chuẩn hóa nội dung các cột dạng chuỗi
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].apply(lambda value: value.strip() if isinstance(value, str) else value)
        # Chuyển chuỗi rỗng thành NULL
        df[col] = df[col].replace("", np.nan)
    return df

# 4. CHUYỂN ĐỔI KIỂU DỮ LIỆU SỐ
def convert_numeric(df, columns, sheet_name):
    """
    Chuyển các cột số sang kiểu numeric.
    Giá trị không hợp lệ được ghi nhận, không tự đổi thành 0.
    """
    df = df.copy()
    for col in columns:
        if col not in df.columns:
            continue
        original = df[col].copy()
        # Loại bỏ dấu phẩy phân cách hàng nghìn
        normalized = (original.astype("string").str.strip().str.replace(",", "", regex=False))
        converted = pd.to_numeric(normalized, errors="coerce")
        # Có dữ liệu ban đầu nhưng không chuyển được sang số
        invalid_mask = original.notna() & converted.isna()
        for index in df.index[invalid_mask]:
            invalid_numeric_cells.add((sheet_name, col, index))
            errors.append({
                "Sheet": sheet_name,
                "Row": int(index) + 2,
                "Column": col,
                "OriginalValue": original.loc[index],
                "Error": "Không chuyển đổi được sang kiểu số"
            })
        df[col] = converted
    return df

# 5. XỬ LÝ VÀ THỐNG KÊ NULL
def handle_null(df, sheet_name):
    """
    Thống kê giá trị NULL.
    Chỉ điền 0 cho các cột đã được xác nhận là chưa phát sinh.
    Không tự tạo mã SKU hoặc mã nhà cung cấp.
    """
    df = df.copy()
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count > 0:
            quality.append({
                "Sheet": sheet_name,
                "Check": "NULL",
                "Column": col,
                "Before": len(df),
                "IssueCount": null_count,
                "After": len(df),
                "Note": "Ghi nhận giá trị thiếu"
            })
    # Chỉ điền 0 cho NULL ban đầu, không điền cho ô lỗi chuyển đổi
    for col in ZERO_IF_NOT_GENERATED:
        if col not in df.columns:
            continue
        for index in df.index[df[col].isna()]:
            if (sheet_name, col, index) not in invalid_numeric_cells:
                df.loc[index, col] = 0
    return df

# 6. KIỂM TRA VÀ LOẠI BỎ DỮ LIỆU TRÙNG LẶP
def remove_duplicates(df, sheet_name):
    """Loại bỏ các dòng trùng lặp hoàn toàn."""
    before = len(df)
    duplicated_count = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    quality.append({
        "Sheet": sheet_name,
        "Check": "Duplicate",
        "Column": "All columns",
        "Before": before,
        "IssueCount": duplicated_count,
        "After": len(df),
        "Note": "Loại bỏ các dòng trùng lặp hoàn toàn"
    })
    return df

# 7. KIỂM TRA VALIDATION
def validate_data(df, sheet_name):
    """Kiểm tra giá trị âm và tính hợp lệ của InventoryValue."""
    df = df.copy()
    # Kiểm tra các cột không được có giá trị âm
    for col in NON_NEGATIVE_COLUMNS:
        if col not in df.columns:
            continue
        invalid_mask = df[col].notna() & (df[col] < 0)
        for index in df.index[invalid_mask]:
            errors.append({
                "Sheet": sheet_name,
                "Row": int(index) + 2,
                "Column": col,
                "OriginalValue": df.loc[index, col],
                "Error": "Giá trị không được nhỏ hơn 0"
            })
    # Kiểm tra InventoryValue = StockQuantity * BaseCost
    required_columns = ["StockQuantity", "BaseCost", "InventoryValue"]
    if all(col in df.columns for col in required_columns):
        expected_value = df["StockQuantity"] * df["BaseCost"]
        invalid_mask = (df["InventoryValue"].notna() & expected_value.notna() & ~np.isclose(df["InventoryValue"], expected_value, rtol=0.000001, atol=0.01))
        for index in df.index[invalid_mask]:
            errors.append({
                "Sheet": sheet_name,
                "Row": int(index) + 2,
                "Column": "InventoryValue",
                "OriginalValue": df.loc[index, "InventoryValue"],
                "Error": "Không khớp StockQuantity * BaseCost"
            })
    return df

# 8. HÀM TÌM TÊN CỘT THEO CÁC TÊN CÓ THỂ CÓ
def find_column(df, candidates):
    """Tìm cột theo danh sách tên thay thế."""
    column_map = {
        str(col).strip().lower(): col
        for col in df.columns
    }
    for name in candidates:
        if name.lower() in column_map:
            return column_map[name.lower()]
    return None

# 9. KIỂM TRA LOOKUP GIỮA CÁC BẢNG
def check_lookup(inventory, sku, vendor):
    """
    Đối chiếu:
    - Sku_code trong Inventory data với SKU Masterdata.
    - PrimaryVendor trong SKU Masterdata với VendorMasterdata.
    """
    # 9.1. Đối chiếu mã SKU
    inventory_sku = find_column(inventory,["Sku_code", "SkuCode", "SKU"])
    master_sku = find_column(sku,["Sku_code", "SkuCode", "SKU"])
    if inventory_sku and master_sku:
        valid_sku = set(sku[master_sku].dropna().astype(str).str.strip())
        invalid_mask = (inventory[inventory_sku].notna() & ~inventory[inventory_sku].astype(str).str.strip().isin(valid_sku))
        for index in inventory.index[invalid_mask]:
            lookup_errors.append({
                "Sheet": "Inventory data",
                "Row": int(index) + 2,
                "Column": inventory_sku,
                "Value": inventory.loc[index, inventory_sku],
                "Error": "Không tìm thấy mã SKU trong SKU Masterdata"
            })

    # 9.2. Đối chiếu PrimaryVendor với VendorMasterdata
    primary_vendor = find_column(sku,["PrimaryVendor", "VendorCode"])
    vendor_code = find_column(vendor,["VendorCode", "Vendor_code", "VendorID"])
    if primary_vendor and vendor_code:
        valid_vendor = set(vendor[vendor_code].dropna().astype(str).str.strip())
        invalid_mask = (sku[primary_vendor].notna() & ~sku[primary_vendor].astype(str).str.strip().isin(valid_vendor))
        for index in sku.index[invalid_mask]:
            lookup_errors.append({
                "Sheet": "SKU Masterdata",
                "Row": int(index) + 2,
                "Column": primary_vendor,
                "Value": sku.loc[index, primary_vendor],
                "Error": "Không tìm thấy nhà cung cấp trong VendorMasterdata"
            })

    # Ghi nhận trường hợp không tìm thấy cột để đối chiếu
    if not inventory_sku or not master_sku:
        lookup_errors.append({
            "Sheet": "Inventory data",
            "Row": None,
            "Column": "Sku_code",
            "Value": None,
            "Error": "Không tìm thấy cột mã SKU phù hợp để Lookup"
        })

    if not primary_vendor or not vendor_code:
        lookup_errors.append({
            "Sheet": "SKU Masterdata",
            "Row": None,
            "Column": "PrimaryVendor",
            "Value": None,
            "Error": "Không tìm thấy cột mã nhà cung cấp phù hợp để Lookup"
        })

# 10. HÀM CHẠY TIỀN XỬ LÝ
def main():
    # Kiểm tra file đầu vào
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Không tìm thấy file đầu vào: {INPUT_FILE}")
    # Kiểm tra các sheet trong file Excel
    excel = pd.ExcelFile(INPUT_FILE)
    missing_sheets = [
        sheet for sheet in SHEETS
        if sheet not in excel.sheet_names
    ]
    if missing_sheets:
        raise ValueError(f"Không tìm thấy các sheet: {missing_sheets}")
    data = {}
    # Đọc và tiền xử lý từng sheet
    for sheet_name in SHEETS:
        df = pd.read_excel(
            excel,
            sheet_name=sheet_name,
            dtype=object
        )
        # Bước 1: Chuẩn hóa dữ liệu chuỗi
        df = clean_text(df)
        # THỐNG KÊ TRƯỚC TIỀN XỬ LÝ
        rows_before = len(df)
        columns_count = len(df.columns)
        missing_before = int(df.isna().sum().sum())
        # Bước 2: Chuyển đổi kiểu dữ liệu số
        df = convert_numeric(df, NUMERIC_COLUMNS, sheet_name)
        # Bước 3: Xử lý NULL
        df = handle_null(df, sheet_name)
        # Đếm số dòng trùng lặp hoàn toàn
        duplicate_count = int(df.duplicated().sum())
        # Bước 4: Loại bỏ dòng trùng lặp
        df = remove_duplicates(df, sheet_name)
        # Bước 5: Kiểm tra Validation
        df = validate_data(df, sheet_name)
        # THỐNG KÊ SAU TIỀN XỬ LÝ
        rows_after = len(df)
        missing_after = int(df.isna().sum().sum())
        # Lưu thống kê của từng sheet
        summary.append({
            "Sheet": sheet_name,
            "Rows before": rows_before,
            "Rows after": rows_after,
            "Exact duplicate rows removed": duplicate_count,
            "Columns": columns_count,
            "Missing cells before": missing_before,
            "Missing cells after": missing_after
        })

        data[sheet_name] = df

    # Bước 6: Kiểm tra Lookup giữa các bảng
    check_lookup(
        data["Inventory data"],
        data["SKU Masterdata"],
        data["VendorMasterdata"]
    )

    # Chuyển danh sách thành DataFrame
    summary_df = pd.DataFrame(summary)
    error_df = pd.DataFrame(errors)
    lookup_df = pd.DataFrame(lookup_errors)
    quality_df = pd.DataFrame(quality)

    # 11. XUẤT FILE EXCEL KẾT QUẢ
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        # Xuất các sheet dữ liệu sau tiền xử lý
        for sheet_name, df in data.items():
            df.to_excel(
                writer,
                sheet_name=sheet_name[:31],
                index=False
            )
        # Xuất sheet thống kê tổng quan
        summary_df.to_excel(
            writer,
            sheet_name="Data_Quality_Summary",
            index=False
        )
        # Xuất báo cáo chất lượng dữ liệu
        quality_df.to_excel(
            writer,
            sheet_name="Data_Quality",
            index=False
        )
        # Xuất danh sách lỗi dữ liệu
        error_df.to_excel(
            writer,
            sheet_name="Data_Errors",
            index=False
        )
        # Xuất danh sách lỗi Lookup
        lookup_df.to_excel(
            writer,
            sheet_name="Lookup_Errors",
            index=False
        )

    # 12. HIỂN THỊ KẾT QUẢ
    print("\nHOÀN THÀNH TIỀN XỬ LÝ DỮ LIỆU")
    print("-" * 45)
    for sheet_name, df in data.items():
        print(f"{sheet_name}: {len(df)} dòng")
    print("-" * 45)
    print(f"Số lỗi dữ liệu: {len(errors)}")
    print(f"Số lỗi Lookup: {len(lookup_errors)}")
    print("\nTHỐNG KÊ TỔNG QUAN:")
    print(summary_df.to_string(index=False))
    print("-" * 45)
    print(f"File kết quả: {OUTPUT_FILE}")

# Chạy chương trình
if __name__ == "__main__":
    main()
