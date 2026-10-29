import pandas as pd

file_path = "D:/KDL/data1.xlsx" #đổi đường dẫn tuỳ theo chỗ mng lưu nhe

# Đọc và kiểm tra các sheet từ file Excel
df_inventory = pd.read_excel(file_path, sheet_name="Inventory data")
df_sku = pd.read_excel(file_path, sheet_name="SKU Masterdata")
df_vendor = pd.read_excel(file_path, sheet_name="VendorMasterdata")

print("--- SKU Masterdata ---")
print(df_sku.head(2))

print("--- VendorMasterdata ---")
print(df_vendor.head(2))

print("--- Inventory data ---")
print(df_inventory.head(2))
