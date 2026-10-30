# Domain: Mechanical Design System

Gói sơ đồ của domain pack `mechanical-design` (MCAD, cặp với `pcb-design` là ECAD): thiết kế cơ khí cho sản phẩm phần cứng. Sơ đồ hiện tập trung vào vỏ sản phẩm, từ kiểu dáng và chia mảnh tới mô hình CAD tham số, mẫu in 3D, khuôn ép và mẫu T1. Quy ước và cách build: [.archify/README.md](../../.archify/README.md). Mô hình khái quát dùng chung: [docs/core-model.md](../../docs/core-model.md).

## Sơ đồ

| # | Sơ đồ | Loại | Nguồn | Xem |
| --- | --- | --- | --- | --- |
| 01 | Tổng quan 4 khối, thêm phần sản xuất (nhà làm khuôn, kết quả mẫu) | architecture | [src](src/01-overview.architecture.json) | [dist](dist/01-overview.html) |
| 02 | Vòng lặp một mẫu vỏ: kiến trúc → duyệt kiểu dáng → CAD → kiểm hình học → review → in 3D → chốt thiết kế → khuôn + mẫu T1 → luật DFM | workflow | [src](src/02-feature-loop.workflow.json) | [dist](dist/02-feature-loop.html) |

## 4 khối của domain

| Khối | Nội dung trong domain này |
| --- | --- |
| **1 · Tri thức** | Datasheet vật liệu, dung sai và năng lực nhà cung cấp, mô hình STEP của linh kiện (chỉ trích xuất) · Hướng dẫn DFM cho ép phun, in 3D, CNC; kinh nghiệm thiết kế nhựa, lắp ghép, GD&T (chưng cất) · Tiêu chuẩn chọn theo sản phẩm: IP (IEC 60529), thử rơi, chống cháy (UL 94), an toàn đồ chơi · Tri thức nội bộ: decisions, lỗi từng lần mẫu, luật DFM nội bộ |
| **2 · Agent & công cụ** | Code-CAD (CadQuery, FreeCAD script) để mô hình tham số sửa và review được như code · kiểm hình học (va chạm với PCB, khe hở, độ dày thành, góc thoát khuôn) · mô phỏng FEA (thử rơi, ứng suất ở lẫy gài, trụ vít) · in 3D lắp thử |
| **3 · Workflow** | planner (chia mảnh, vật liệu, cách lắp) → duyệt kiểu dáng → builder (CAD tham số + bản vẽ) → kiểm hình học → reviewer (DFM, lắp ráp, an toàn) → mẫu in 3D (bỏ qua khi không đổi hình dáng) → verifier → chốt thiết kế → khuôn + mẫu T1 → verifier (rơi, IP, ngoại quan) → curator (lỗi → luật DFM) |
| **4 · Mô hình hoá domain** | Hai tầng mẫu vật lý: in 3D nhanh và rẻ, khuôn ép chậm và rất đắt · Kiểu dáng và màu sắc là phán đoán của người · Sau khi có khuôn chỉ sửa theo hướng bớt thép (steel safe), không rollback · Biên PCB, lỗ bắt vít, vị trí cổng và nút là artefact chung với `pcb-design` |

## So với các domain đã có

| | `embedded-mcu` | `llm-agent` | `pcb-design` | `mechanical-design` |
| --- | --- | --- | --- | --- |
| Artefact | firmware | code, prompt, cấu hình, model | schematic, layout, BOM | mô hình CAD, bản vẽ, BOM cơ khí, CMF |
| Kiểm chứng nhanh | build, test, bộ nhớ | lint, unit | ERC, DRC/DFM, kiểm BOM | kiểm hình học, FEA |
| Kiểm chứng chậm | HIL bench | eval chậm | sản xuất + bring-up | in 3D (giờ), rồi khuôn + mẫu T1 (tuần) |
| Bằng chứng phán đoán | ít | LLM judge | review layout | kiểu dáng, cảm giác cầm, ngoại quan |
| Sau phát hành | OTA, rollback | canary, rollback | rework hoặc rev mới | sửa khuôn bớt thép hoặc khuôn mới |

Cả bốn gói dùng cùng các khái niệm của mô hình khái quát; khác nhau ở giá trị, không ở cấu trúc.

## Ghi chú

- Tiêu chuẩn IEC, UL và an toàn đồ chơi có bản quyền: chỉ dùng nội bộ, skill chỉ giữ mã điều khoản và diễn giải do nhóm tự viết.
- Agent làm được nhiều nhất khi mô hình là code-CAD có tham số; với CAD dạng file nhị phân, agent chủ yếu chạy kiểm tra và sinh bản vẽ, BOM.
- Tên agent, vị trí cổng duyệt và các công cụ là đề xuất, chưa chốt.
