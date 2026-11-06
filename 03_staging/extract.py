import pandas as pd
from pathlib import Path

# Khai báo đường dẫn
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR.parent / "01_data" / "raw" / "data1.xlsx"

# Kiểm tra file đầu vào
if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Không tìm thấy file: {INPUT_FILE}")

# Đọc và kiểm tra các sheet từ file Excel
df_inventory = pd.read_excel(INPUT_FILE, sheet_name="Inventory data")
df_sku = pd.read_excel(INPUT_FILE, sheet_name="SKU Masterdata")
df_vendor = pd.read_excel(INPUT_FILE, sheet_name="VendorMasterdata")

print("--- SKU Masterdata ---")
print(df_sku.head(2))

print("--- VendorMasterdata ---")
print(df_vendor.head(2))

print("--- Inventory data ---")
print(df_inventory.head(2))
