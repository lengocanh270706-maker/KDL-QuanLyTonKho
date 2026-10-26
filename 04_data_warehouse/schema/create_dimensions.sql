USE EcommerceLogistics;
GO

-- Tạo bảng chiều SKU (Dim_SKU)
CREATE TABLE Dim_SKU (
    Sku_Code NVARCHAR(100) PRIMARY KEY,
    Sku_Name NVARCHAR(500),
    SKU_Short_Name NVARCHAR(200),
    Primary_Vendor NVARCHAR(200),
    Brand NVARCHAR(200),
    Sale_Price DECIMAL(18, 2),
    Base_Cost DECIMAL(18, 2)
);

-- Tạo bảng chiều Nhà cung cấp (Dim_Vendor)
CREATE TABLE Dim_Vendor (
    Vendor_Name NVARCHAR(200) PRIMARY KEY
);
GO
