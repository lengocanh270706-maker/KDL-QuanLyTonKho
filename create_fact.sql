USE EcommerceLogistics;
GO

-- Bảng Sự kiện Tồn kho (Fact_Inventory_Snapshot)
CREATE TABLE Fact_Inventory_Snapshot (
    SnapshotID INT IDENTITY(1,1) PRIMARY KEY,
    
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