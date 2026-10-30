# Domain: Embedded MCU System

Gói sơ đồ của domain pack `embedded-mcu`: dự án lập trình nhúng / IoT (thiết kế mạch + firmware). Quy ước và cách build: [.archify/README.md](../../.archify/README.md).

## Sơ đồ

| # | Sơ đồ | Loại | Nguồn | Xem |
| --- | --- | --- | --- | --- |
| 01 | Tổng quan 4 khối, thêm phần vận hành (thiết bị hiện trường, telemetry) | architecture | [src](src/01-overview.architecture.json) | [dist](dist/01-overview.html) |
| 02 | Vòng lặp một tính năng firmware: spec → duyệt → code + doc → kiểm nhanh → review → HIL (khi cần) → duyệt merge → OTA theo đợt → giữ hay rollback → học lại | workflow | [src](src/02-feature-loop.workflow.json) | [dist](dist/02-feature-loop.html) |

## 4 khối của domain

| Khối | Nội dung trong domain này |
| --- | --- |
| **1 · Tri thức** | Datasheet, errata, TRM, SVD, header SDK của hãng (chỉ trích xuất, tra kèm số trang) · Sách kỹ thuật nhúng (RTOS, driver, low-power) · Tiêu chuẩn bật theo mức an toàn: MISRA C, IEC 61508, ISO 26262 · Kiến trúc tham chiếu: AUTOSAR, HAL/BSP phân lớp · Tri thức nội bộ: decisions, issues, evals, dấu hiệu lỗi đã biết (chuỗi log → nguyên nhân → trạng thái) |
| **2 · Agent & công cụ** | archify (sơ đồ) · gitnexus (impact analysis) · phân tích tĩnh (cppcheck, chỉ phủ một phần MISRA C) · báo cáo bộ nhớ (RAM/flash/stack so với base) · HIL bench kèm đo dòng · [ponytail](https://github.com/DietrichGebert/ponytail): kỷ luật viết code của `builder` (skill), không phải cổng kiểm chứng |
| **3 · Workflow** | planner → duyệt thiết kế → builder (code + doc) → kiểm nhanh (build, host test, ngân sách bộ nhớ, kiểm tĩnh) → reviewer → HIL (khi đổi driver/ISR/power/OTA) → verifier → duyệt merge → OTA theo đợt + telemetry → verifier (giữ hay rollback) → curator (crash → lỗi đã biết). Tối đa 3 vòng quay lại builder |
| **4 · Mô hình hoá domain** | Mức an toàn khai báo trong `domain.toml` (không yêu cầu / SIL / ASIL) quyết định tiêu chuẩn và quy trình khung (V-model ASPICE chỉ khi cần) · Vòng kiểm chứng: build, test, bộ nhớ, HIL, năng lượng (nhanh với firmware, chậm với phần cứng) · Cổng người duyệt: thiết kế và merge · Promotion: bài học đúng ở ≥ 2 dự án đề xuất lên pack, người duyệt mới nhận |

## Ghi chú

- Tiêu chuẩn ISO 26262, MISRA C và AUTOSAR có bản quyền: chỉ dùng nội bộ, không chưng cất nguyên văn; skill chỉ giữ mã quy tắc và diễn giải do nhóm tự viết.
- Chính sách HIL: bench bận hoặc hỏng thì `verifier` trả BLOCKED; người duyệt merge quyết chờ hay nhận rủi ro, BLOCKED không bao giờ ghi thành PASS.
- **Chưa chốt:** phạm vi phần cứng. Đề xuất: phần thiết kế mạch tách thành domain riêng [pcb-design](../pcb-design/README.md), domain này thu về firmware; pin map và power tree là artefact chung của hai domain.
- `planner` là vai trò thực hiện bước loại `design` của domain này; dự án nhúng khác có thể không cần ([docs/core-model.md §3](../../docs/core-model.md#3-bước-một-khái-niệm-thay-cho-mọi-slot)).
- Tên agent và vị trí cổng duyệt là đề xuất, chưa chốt ([docs/architecture.md §4](../../docs/architecture.md#4-agent-4-vai-trò-chung-chuyên-môn-hoá-bằng-checklist)).
