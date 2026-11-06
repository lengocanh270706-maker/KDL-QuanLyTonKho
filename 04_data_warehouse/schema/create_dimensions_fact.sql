USE EcommerceLogistics;
GO

-- Xóa bảng cũ nếu tồn tại
DROP TABLE IF EXISTS Fact_Inventory;
DROP TABLE IF EXISTS Dim_Product;
DROP TABLE IF EXISTS Dim_Supplier;
DROP TABLE IF EXISTS Dim_Channel;
DROP TABLE IF EXISTS Dim_Shop;

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

-- Bảng Sự kiện Tồn kho (Fact_Inventory)
CREATE TABLE Fact_Inventory (
    InventoryID INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Khóa ngoại liên kết Dim (Surrogate Keys)
    ProductKey INT NOT NULL FOREIGN KEY REFERENCES Dim_Product(ProductKey),
    ChannelKey INT NOT NULL FOREIGN KEY REFERENCES Dim_Channel(ChannelKey),
    ShopKey INT NULL FOREIGN KEY REFERENCES Dim_Shop(ShopKey),
    
    -- Measures (Chỉ số đo lường)
    StockQuantity DECIMAL(18,2) DEFAULT 0,
    MonthlyDemand DECIMAL(18,4) DEFAULT 0,
    DOITargetDays DECIMAL(10,2) DEFAULT 0,
    InventoryValue DECIMAL(18,2) NULL -- StockQuantity * BaseCost
);
GO
