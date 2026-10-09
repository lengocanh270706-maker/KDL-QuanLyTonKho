# KDL-QuanLyTonKho

**Đề tài:** Xây dựng kho dữ liệu và hệ thống hỗ trợ ra quyết định trong quản lý tồn kho cho sàn thương mại điện tử.

## 1. Giới thiệu

Dự án xây dựng kho dữ liệu và hệ thống hỗ trợ ra quyết định nhằm hỗ trợ quản lý tồn kho trong lĩnh vực thương mại điện tử. Hệ thống tập trung thu thập, xử lý và tổ chức dữ liệu để phục vụ phân tích tình hình tồn kho, theo dõi sản phẩm và hỗ trợ đưa ra quyết định quản lý.

## 2. Mục tiêu

- Thu thập và khảo sát dữ liệu từ bộ dữ liệu được lựa chọn.
- Xây dựng quy trình ETL (Extract, Transform, Load).
- Thiết kế và xây dựng kho dữ liệu trên SQL Server.
- Xây dựng các bảng Fact và Dimension phục vụ phân tích.
- Phân tích dữ liệu và xây dựng dashboard hỗ trợ ra quyết định.

## 3. Công nghệ dự kiến

- **Python:** Khảo sát, xử lý và làm sạch dữ liệu.
- **SQL Server:** Lưu trữ Staging và kho dữ liệu.
- **SSIS hoặc Python:** Thực hiện quy trình ETL.
- **Power BI:** Trực quan hóa dữ liệu và xây dựng dashboard.
- **GitHub:** Quản lý mã nguồn và phối hợp làm việc nhóm.

## 4. Các giai đoạn thực hiện

1. Khảo sát yêu cầu và tìm hiểu bộ dữ liệu.
2. Phân tích dữ liệu và xây dựng Data Dictionary.
3. Thiết kế mô hình kho dữ liệu.
4. Xây dựng Staging và quy trình ETL.
5. Nạp dữ liệu vào kho dữ liệu.
6. Phân tích dữ liệu và xây dựng dashboard hỗ trợ ra quyết định.
7. Kiểm thử, đánh giá và hoàn thiện báo cáo.


**Dataset dùng chung:** `01_data/raw/`
Các thành viên sử dụng cùng nguồn dữ liệu. Không tự ý thay đổi dữ liệu gốc; dữ liệu sau xử lý được lưu trong `01_data/processed/`.
## Phân công
| Thành viên | Thư mục phụ trách | Nhiệm vụ chính |
|---|---|---|
| 2 | `02_analysis/` | Khảo sát dữ liệu, thống kê số dòng, cột, kiểu dữ liệu, NULL và dữ liệu trùng |
| 3 | `03_staging/` | Trích xuất dữ liệu, tạo bảng Staging và nạp dữ liệu vào SQL Server |
| 3 | `04_data_warehouse/` | Thiết kế, tạo bảng Dimension, Fact và nạp dữ liệu vào Data Warehouse |
| 4 | `05_etl/` | Làm sạch dữ liệu, xử lý NULL, Duplicate, sai kiểu dữ liệu, Lookup, Validation và tích hợp pipeline ETL |
| 4 | `06_olap_dss/` | Truy vấn phân tích dữ liệu, xây dựng nội dung OLAP/DSS và hỗ trợ ra quyết định tồn kho |

## Cấu trúc thư mục
```text
KDL-QuanLyTonKho/
├── 01_data/
│   ├── raw/
│   └── processed/
├── 02_analysis/
├── 03_staging/
├── 04_data_warehouse/
│   ├── schema/
│   └── load/
├── 05_etl/
├── 06_olap_dss/
├── .gitignore
└── README.md
```

## Quy định thực hiện
Mỗi thành viên chịu trách nhiệm chính đối với thư mục được phân công. Khi cần chỉnh sửa thư mục của thành viên khác, cần trao đổi trước với nhóm.
Trong mỗi phần, ưu tiên tổ chức các file như sau:
- File `.py`: code xử lý dữ liệu.
- File `.sql`: tạo bảng, truy vấn hoặc kiểm tra dữ liệu.
