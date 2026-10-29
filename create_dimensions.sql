USE EcommerceLogistics;
GO

-- Xóa bảng cũ nếu tồn tại
IF OBJECT_ID('Fact_Inventory_Snapshot', 'U') IS NOT NULL DROP TABLE Fact_Inventory_Snapshot;
IF OBJECT_ID('Dim_Product', 'U') IS NOT NULL DROP TABLE Dim_Product;
IF OBJECT_ID('Dim_Supplier', 'U') IS NOT NULL DROP TABLE Dim_Supplier;
IF OBJECT_ID('Dim_Channel', 'U') IS NOT NULL DROP TABLE Dim_Channel;
IF OBJECT_ID('Dim_Shop', 'U') IS NOT NULL DROP TABLE Dim_Shop;

-- 1. Dim_Product (Chiều Sản Phẩm)
CREATE TABLE Dim_Product (
    ProductKey INT IDENTITY(1,1) PRIMARY KEY,
    SkuCode NVARCHAR(100) NOT NULL,
    SkuName NVARCHAR(MAX),
    SKUShortName NVARCHAR(255),
    Brand NVARCHAR(100),
    SalePrice DECIMAL(18,2),
    BaseCost DECIMAL(18,2),
    PrimaryVendor NVARCHAR(255)
);

-- 2. Dim_Supplier (Chiều Nhà Cung Cấp)
CREATE TABLE Dim_Supplier (
    SupplierKey INT IDENTITY(1,1) PRIMARY KEY,
    VendorCode NVARCHAR(100) NOT NULL,
    VendorName NVARCHAR(255),
    ShippingAddress NVARCHAR(MAX),
    PaymentTermsPerWeek DECIMAL(10,2)
);

-- 3. Dim_Channel 
CREATE TABLE Dim_Channel (
    ChannelKey INT IDENTITY(1,1) PRIMARY KEY,
    ChannelName NVARCHAR(100) NOT NULL UNIQUE 
);

-- 4. Dim_Shop 
CREATE TABLE Dim_Shop (
    ShopKey INT IDENTITY(1,1) PRIMARY KEY,
    ShopAccount NVARCHAR(100) NOT NULL
);
GO