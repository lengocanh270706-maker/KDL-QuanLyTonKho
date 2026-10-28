USE EcommerceLogistics;
GO

-- OLAP 1: Tổng hợp tồn kho và nhu cầu theo từng Sàn TMĐT (Roll-up / Aggregation)
SELECT 
    SUM(TRY_CAST(Tiki AS FLOAT)) AS Total_Tiki_Stock,
    SUM(TRY_CAST(Lazada AS FLOAT)) AS Total_Lazada_Stock,
    SUM(TRY_CAST(Shopee AS FLOAT)) AS Total_Shopee_Stock,
    SUM(TRY_CAST(TikTok AS FLOAT)) AS Total_TikTok_Stock,
    SUM(TRY_CAST(Sendo AS FLOAT)) AS Total_Sendo_Stock,
    SUM(TRY_CAST(Tiki_Demand_Per_Month AS FLOAT)) AS Total_Tiki_Demand,
    SUM(TRY_CAST(Shopee_Demand_Per_Month AS FLOAT)) AS Total_Shopee_Demand
FROM Fact_Inventory
WHERE SKU_Code IS NOT NULL;
GO

-- OLAP 2: Phân tích tồn kho và nhu cầu theo từng Thương hiệu 
SELECT 
    Brand,
    ISNULL(SUM(TRY_CAST(Tiki AS FLOAT)), 0) AS Total_Tiki_Stock,
    ISNULL(SUM(TRY_CAST(Lazada AS FLOAT)), 0) AS Total_Lazada_Stock,
    ISNULL(SUM(TRY_CAST(Shopee AS FLOAT)), 0) AS Total_Shopee_Stock,
    ISNULL(SUM(TRY_CAST(TikTok AS FLOAT)), 0) AS Total_TikTok_Stock,
    ISNULL(SUM(TRY_CAST(Sendo AS FLOAT)), 0) AS Total_Sendo_Stock,
    ISNULL(SUM(TRY_CAST(Tiki_Demand_Per_Month AS FLOAT)), 0) AS Total_Tiki_Demand,
    ISNULL(SUM(TRY_CAST(Shopee_Demand_Per_Month AS FLOAT)), 0) AS Total_Shopee_Demand
FROM Fact_Inventory
WHERE Brand IS NOT NULL AND LTRIM(RTRIM(Brand)) <> ''
GROUP BY Brand
ORDER BY Brand;
GO

-- OLAP 3: Thống kê hiệu suất theo Nhà cung cấp (Vendor Performance)
SELECT 
    f.Vendor AS Vendor_Name,
    COUNT(f.SKU_Code) AS Product_Count,
    SUM(
        ISNULL(TRY_CAST(f.Tiki AS FLOAT), 0) + 
        ISNULL(TRY_CAST(f.Lazada AS FLOAT), 0) + 
        ISNULL(TRY_CAST(f.Shopee AS FLOAT), 0) + 
        ISNULL(TRY_CAST(f.TikTok AS FLOAT), 0) + 
        ISNULL(TRY_CAST(f.Sendo AS FLOAT), 0)
    ) AS Total_Inventory_Across_Platforms
FROM Fact_Inventory f
WHERE f.Vendor IS NOT NULL
GROUP BY f.Vendor
ORDER BY Total_Inventory_Across_Platforms DESC;
GO

-- OLAP 4: Lọc danh sách sản phẩm có chỉ tiêu DOI thấp 
SELECT TOP 20
    f.SKU_Code,
    ISNULL(d.Sku_Name, N'Chưa có tên trong Dim_SKU') AS Sku_Name,
    f.Shop_Account,
    TRY_CAST(f.Shopee AS FLOAT) AS Shopee_Stock,
    TRY_CAST(f.Shopee_Demand_Per_Month AS FLOAT) AS Shopee_Demand,
    TRY_CAST(f.DOI_Target_Days AS FLOAT) AS DOI_Target_Days,
    f.Vendor
FROM Fact_Inventory f
LEFT JOIN Dim_SKU d ON LTRIM(RTRIM(f.SKU_Code)) = LTRIM(RTRIM(d.Sku_Code))
WHERE f.DOI_Target_Days IS NOT NULL
ORDER BY TRY_CAST(f.DOI_Target_Days AS FLOAT) ASC;
GO
