USE EcommerceLogistics;
GO

-- 1. Xóa bảng staging cũ nếu tồn tại
DROP TABLE IF EXISTS stg_InventoryData;
DROP TABLE IF EXISTS stg_SKUMasterdata;
DROP TABLE IF EXISTS stg_VendorMasterdata;
GO

-- 2. Tạo các bảng Staging 
CREATE TABLE stg_InventoryData (
    [Sku_name] NVARCHAR(MAX),
    [Sku_code] NVARCHAR(MAX),
    [shop_account] NVARCHAR(MAX),
    [Tiki] NVARCHAR(MAX),
    [Lazada] NVARCHAR(MAX),
    [Shopee] NVARCHAR(MAX),
    [TikTok] NVARCHAR(MAX),
    [Sendo] NVARCHAR(MAX),
    [Tiki demand per...] NVARCHAR(MAX),
    [Lazada demand per...] NVARCHAR(MAX),
    [Shopee demand per...] NVARCHAR(MAX),
    [TikTok demand per...] NVARCHAR(MAX),
    [Sendo demand per...] NVARCHAR(MAX),
    [DOITarget_(days)] NVARCHAR(MAX),
    [Vendor] NVARCHAR(MAX),
    [Brand] NVARCHAR(MAX)
);
GO

CREATE TABLE stg_SKUMasterdata (
    [Sku Code] NVARCHAR(MAX),
    [Sku Name] NVARCHAR(MAX),
    [SKU Short Name] NVARCHAR(MAX),
    [Primary Vendor] NVARCHAR(MAX),
    [Brand] NVARCHAR(MAX),
    [Sale Price] NVARCHAR(MAX),
    [Base Cost] NVARCHAR(MAX)
);
GO

CREATE TABLE stg_VendorMasterdata (
    [Vendor] NVARCHAR(MAX)
);
GO
