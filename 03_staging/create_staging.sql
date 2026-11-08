USE EcommerceLogistics_Staging;
GO
--Xoá bảng cũ nếu tồn tại
DROP TABLE IF EXISTS stg_InventoryData;
DROP TABLE IF EXISTS stg_SKUMasterdata;
DROP TABLE IF EXISTS stg_VendorMasterdata;
GO

-- Tạo bảng stg_InventoryData 
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

-- Tạo bảng stg_SKUMasterdata 
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

-- Tạo bảng stg_VendorMasterdata 
CREATE TABLE stg_VendorMasterdata (
    [SHOP_ACCOUNT] NVARCHAR(MAX),
    [VENDOR] NVARCHAR(MAX),
    [BRAND] NVARCHAR(MAX),
    [Vendor Name] NVARCHAR(MAX),
    [Shipping Adress] NVARCHAR(MAX),
    [Payment Terms (per week)] NVARCHAR(MAX)
);
GO
