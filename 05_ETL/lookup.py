import pandas as pd


class SkuLookupManager:

  def __init__(self, df_sku_master):
    """Khởi tạo bộ quản lý tra cứu dựa trên bảng SKU Masterdata."""
    # Tạo sẵn một dictionary tra cứu nhanh: Key là Sku Code, Value là Sku Name
    self.sku_name_map = dict(
        zip(df_sku_master["Sku Code"], df_sku_master["Sku Name"])
    )
    self.brand_map = dict(
        zip(df_sku_master["Sku Code"], df_sku_master["Brand"])
    )

  def get_sku_name(self, sku_code):
    """Tra cứu tên sản phẩm dựa vào mã SKU."""
    return self.sku_name_map.get(sku_code, "Unknown Product")

  def get_brand(self, sku_code):
    """Tra cứu thương hiệu dựa vào mã SKU."""
    return self.brand_map.get(sku_code, "Unknown Brand")


# Hàm tiện ích để kiểm tra tính hợp lệ của mã SKU tồn kho so với Masterdata
def validate_sku_existence(df_inv, df_sku):
  master_skus = set(df_sku["Sku Code"].dropna())
  inv_skus = set(df_inv["Sku_code"].dropna())

  # Tìm các mã SKU xuất hiện ở kho nhưng chưa có trong danh mục Masterdata
  missing_skus = inv_skus - master_skus
  if missing_skus:
    print(
        f"Cảnh báo: Có {len(missing_skus)} mã SKU tồn kho không có trong"
        " Masterdata!"
    )
  else:
    print("Kiểm tra Lookup: Tất cả mã SKU tồn kho đều khớp với Masterdata!")

  return missing_skus