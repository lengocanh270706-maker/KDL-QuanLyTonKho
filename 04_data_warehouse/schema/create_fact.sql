USE EcommerceLogistics;
GO

-- Tạo bảng sự kiện tồn kho (Fact_Inventory)
CREATE TABLE Fact_Inventory (
    Fact_ID INT IDENTITY(1,1) PRIMARY KEY,
    SKU_Code NVARCHAR(500),
    Shop_Account NVARCHAR(200),
    Tiki FLOAT,
    Lazada FLOAT,
    Shopee FLOAT,
    TikTok FLOAT,
    Sendo FLOAT,
    Tiki_Demand_Per_Month FLOAT,
    Lazada_Demand_Per_Month FLOAT,
    Shopee_Demand_Per_Month FLOAT,
    TikTok_Demand_Per_Month FLOAT,
    Sendo_Demand_Per_Month FLOAT,
    DOI_Target_Days FLOAT,
    Vendor NVARCHAR(200),
    Brand NVARCHAR(200)
);
GO
