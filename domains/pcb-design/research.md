# Nghiên cứu nền cho domain `pcb-design` (2026-10)

Ghi chú nghiên cứu làm căn cứ cho [README](README.md) và các sơ đồ của gói. Mỗi ý có nguồn; **[chưa kiểm]** là ý chỉ có nguồn thứ cấp, nguồn của chính nhà bán, hoặc không mở được nguồn gốc. Phần lớn nguồn là blog của hãng EDA, nhà máy và người làm nghề; chưa có nghiên cứu trung lập nào đo tỉ lệ board chạy đúng ngay lần đầu.

## 1. Quy trình một rev board trong thực tế

### 1.1. Giai đoạn và cổng

- Trình tự phổ biến: yêu cầu → kiến trúc → chọn linh kiện → schematic → review schematic → placement → routing → review layout → gửi sản xuất → sản xuất, lắp ráp → bring-up → kiểm định → ECO, rev sau ([Siemens](https://blogs.sw.siemens.com/electronic-systems-design/2022/09/06/what-is-the-pcb-design-process/)).
- Review schematic phải xong và đóng hết ý kiến trước khi bắt đầu layout; review layout làm khi placement đã xong mà routing chưa chốt ([applied-ee](https://applied-ee.github.io/ee-notebook/docs/design-development/schematic-design/early-design-reviews)).
- Điều kiện vào review layout: schematic đã chốt, stackup và datasheet có sẵn, DRC sạch, biên board và lỗ bắt vít đã kiểm ([Cadence](https://resources.pcb.cadence.com/blog/2023-pcb-design-and-risk-benefit-analysis-in-component-placement)).
- Review bắt buộc ở mọi nơi: review schematic và review layout/DFM trước khi gửi sản xuất. Nhóm có quy trình chặt hơn thêm review placement và review routing tín hiệu quan trọng (cùng nguồn Cadence).
- EVT / DVT / PVT là cấp sản phẩm, không phải cấp board: EVT hỏi kiến trúc có chạy trên phần cứng thật không (3–10 mẫu), DVT hỏi thiết kế có bền trong mọi điều kiện, PVT hỏi nhà máy có làm được với tỉ lệ đạt mục tiêu không ([null2one](https://null2one.pages.dev/insights/evt-dvt-pvt-decision-gates/), [Formlabs](https://formlabs.com/global/blog/validation-testing-product-development-poc-evt-dvt-pvt-mp/)). Mỗi giai đoạn thường có một hoặc vài rev board **[chưa kiểm]**.

### 1.2. Placement là một cổng riêng

- Ở dịch vụ thiết kế thuê ngoài, khách hàng phải duyệt placement trước routing, vì đổi netlist hay placement sau đó rất khó ([ALLPCB](https://www.allpcb.com/sns/a-primer-outsourcing-pcb-design_4746.html)).
- Placement quyết định SI, EMI, nhiệt và khả năng sản xuất trước khi có đường mạch nào ([JLCPCB](https://jlcpcb.com/blog/pcb-component-placement-guide-2026), [I-Connect007](https://iconnect007.com/article/146570/beyond-design-effective-floor-planning-strategies/146567/pcb)).
- Stackup phải chốt trước routing vì độ rộng đường mạch và via phụ thuộc vào nó. Đầu vào của cổng placement: stackup, biên cơ khí, vùng cấm.

### 1.3. Rev, gói gửi sản xuất, thay đổi

- Quy ước đặt tên rev khác nhau giữa các nơi; đổi form/fit/function thì đổi mã sản phẩm, còn lại tăng rev ([Jiga](https://jiga.io/articles/engineering-change-orders/)).
- Gói sản xuất mạch in: Gerber X2 hoặc ODB++ hoặc IPC-2581, file khoan, bản vẽ sản xuất (biên, bảng khoan, stackup, ghi chú, cấp IPC-6012, trở kháng), netlist IPC-356 (bắt buộc với Class 3) ([Advanced Circuits](https://www.advancedpcb.com/en-us/resources/blog/pcb-fabrication-drawing-what-it-is-and-what-it-should-include/), [NCAB](https://www.ncabgroup.com/blog/pcb-fabrication-drawing/)).
- Gói lắp ráp: BOM, pick-and-place, bản vẽ lắp ráp có cực tính. Phải kiểm chéo: độ dày trên bản vẽ khớp stackup, rev của BOM khớp rev schematic và gói lắp ráp ([Cadence](https://resources.pcb.cadence.com/home/jbj-section-15-pcb-design-creating-a-document-package)).
- IPC-2581 là định dạng XML mở, mang stackup có cấu trúc; nhà máy prototype giá rẻ còn chậm hỗ trợ ([Altium](https://resources.altium.com/p/pcb-production-file-format-wars)).
- ECR → ECO → ECN: đề nghị, phê duyệt, thông báo. ECN liệt kê mọi mã và rev bị ảnh hưởng, kể cả thay đổi chỉ ở BOM ([Jiga](https://jiga.io/articles/engineering-change-orders/)).
- Deviation duyệt trước khi làm, waiver chấp nhận thứ đã làm; cả hai có hạn và gắn với một dải số serial ([Best PCBs](https://www.bestpcbs.com/blog/2026/08/pcb-engineering-change-order-eco-release-checklist/), blog nhà máy).

### 1.4. Bring-up

- Trình tự: soi bằng mắt, đo điện trở các rail xuống GND (gần 0 Ω thì không cấp nguồn) → cấp nguồn bench có giới hạn dòng → bật từng rail → quét nhiệt → đo áp tại chân IC → kiểm clock → JTAG/SWD, UART, I2C/SPI → kiểm chức năng ([applied-ee](https://applied-ee.github.io/ee-notebook/docs/design-development/prototyping-and-bring-up/bring-up-checklists), [Cadence](https://resources.pcb.cadence.com/blog/the-definitive-guide-to-pcb-bring-up)).
- Kinh nghiệm đáng ghi thành quy tắc: dao động không chạy là rất phổ biến; lỗi giao tiếp thường là lỗi nguồn; bắt đầu danh sách cho rev sau ngay trong lúc bring-up (cùng nguồn applied-ee).
- Mỗi board một nhật ký theo số serial (traveler): rev, rework, sửa chữa ([LIGO eTraveler](https://dcc-llo.ligo.org/public/0021/G1000955/003/eTraveler_v3.pdf), [ví dụ bring-up log](https://bauer-group.github.io/EMB-USBMultiBusBridge/hardware/bringup-log/)). Quyết định rework tiếp hay làm rev mới dựa trên nhật ký này.
- Số liệu respin: trung bình 2,9 lần một dự án (Lifecycle Insights 2018, chỉ có nguồn thứ cấp **[chưa kiểm]**, [Electronic Design](https://www.electronicdesign.com/markets/automation/article/21807687/the-new-shift-left-multi-dimensional-pcb-design-verification-platform)). Nên lập kế hoạch cho ít nhất 2 lần làm mẫu.

### 1.5. Lỗi hay gặp ở lần làm đầu

Không có bộ số liệu xếp hạng; danh sách tổng hợp từ nguồn người làm nghề ([Altium](https://resources.altium.com/p/avoid-first-pass-perils-prototyping-runs-your-electronics), [Altium footprint](https://resources.altium.com/p/diabolical-footprint-mistakes-and-how-avoid-them-altiumlive-2022), [SparkFun](https://sparkfun.com/tutorials/42), [Digi-Key](https://www.digikey.ch/fr/maker/blogs/2018/the-biggest-mistakes-new-makers-make), applied-ee):

1. Footprint sai biến thể, sai chân 1, nhầm hình nhìn từ trên với nhìn từ dưới.
2. Đảo chân (transistor, regulator, header).
3. Thiếu hoặc mập mờ ký hiệu cực tính.
4. Pinout connector board-to-board không khớp.
5. Tên net và port không khớp giữa các sheet phân cấp.
6. Dao động, thạch anh không chạy.
7. Thiếu pull-up/pull-down ở reset, chân boot, ngắt.
8. Thiếu tụ lọc nguồn, chập rail.
9. Sai thứ tự bật nguồn, chân enable.
10. Vành khuyên không đủ, khoan lệch, chạm chân BGA.

### 1.6. Rủi ro chuỗi cung ứng

- Vòng đời (Active / NRND / EOL) là cổng ở bước chọn linh kiện, khi layout còn đổi được; tra trang của hãng vì dữ liệu nhà phân phối chậm hơn ([applied-ee](https://applied-ee.github.io/ee-notebook/docs/design-development/part-selection-and-sourcing/lifecycle-status)).
- Linh kiện vừa NRND/EOL, vừa lead time ≥ 12 tuần, vừa một nguồn thì phải có linh kiện thay thế trước khi chốt, hoặc kế hoạch mua lần cuối ([Cofactr](https://www.cofactr.com/blog/how-i-learned-to-stop-worrying-and-love-the-bom-scrub), quy tắc của một nhà bán).
- Kiểm hai lần: lúc chốt schematic (vòng đời, số nguồn, linh kiện thay thế) và lúc gửi sản xuất (tồn kho, lead time, giá theo số lượng). Mẫu hai lần này lặp lại ở nhiều nguồn nhưng không phải tiêu chuẩn ([Venture](https://www.venture-mfg.com/prevent-supply-chain-delays-pcb-assembly/), [Altium](https://resources.altium.com/p/pcb-supply-chain-review)).
- Khoảng 82.200 thay đổi vòng đời năm 2023 không đi kèm PCN, nên phải chủ động tra trạng thái, không chỉ chờ thông báo ([Z2Data](https://www.z2data.com/insights/82-000-product-lifecycle-changes-in-2023-had-no-pcn)).

### 1.7. Tiêu chuẩn và lúc cần

| Tiêu chuẩn | Quy định gì | Bước |
| --- | --- | --- |
| IPC-7351 | hình học land pattern (footprint) SMT | thư viện |
| IPC-2221 / 2222 | luật thiết kế chung, khoảng cách, creepage | layout |
| IPC-2152 | dòng chịu được của đường mạch và mặt đồng theo độ tăng nhiệt | layout, nhánh nguồn |
| IPC-2581 | định dạng dữ liệu sản xuất mở | gửi sản xuất |
| IPC-6012 | chất lượng board trần Class 1/2/3 | ghi trên bản vẽ sản xuất |
| IPC-A-600 / IPC-A-610 | tiêu chí ngoại quan board trần / board đã lắp | nhận hàng, gửi nhà lắp ráp |
| J-STD-001 | quy trình hàn (IPC-A-610 là tiêu chí chấm kết quả) | nhà lắp ráp |
| IPC-1752B, RoHS, REACH | khai báo vật liệu, chất cấm | chọn linh kiện và gửi sản xuất |
| CISPR 32, IEC 61000-4-x | phát xạ, miễn nhiễm **[chưa kiểm]** | pre-scan từ mẫu chạy được đầu tiên |
| IEC 62368-1 | an toàn thiết bị ICT/AV, ảnh hưởng tới kiến trúc (cách điện, creepage) | kiến trúc, DVT |

Nguồn: [Wevolver](https://www.wevolver.com/article/mastering-ipc-standards-the-definitive-guide-for-electronics-engineers-and-pcb-designers), [IPC](https://www.electronics.org/materials-declaration-data-exchange-standards-homepage), [Digi-Key](https://www.digikey.at/en/articles/iec-62368-1-is-on-its-way-the-new-safety-standard-ict-av-equipment), [In Compliance](https://incompliancemag.com/preparing-for-compliance-testing-a-step-by-step-guide-for-engineers-in-product-development-and-emc-safety-certification/). Bộ tối thiểu cho nhóm nhỏ (tổng hợp, không phải quy định): IPC-7351, 2221, 2152 khi layout; IPC-6012 Class 2 và IPC-A-610 Class 2 khi gửi sản xuất; RoHS/REACH ở BOM; pre-scan EMC từ EVT.

## 2. Công cụ chạy không cần giao diện (KiCad, 2026-10)

KiCad 10.0 ra tháng 3/2026, bản vá mới nhất 10.0.6 tháng 8/2026 ([KiCad](https://www.kicad.org/blog/2026/08/KiCad-10.0.6-Release/)).

| Việc | Công cụ | Làm cổng được? | Nguồn |
| --- | --- | --- | --- |
| ERC, DRC | `kicad-cli sch erc`, `kicad-cli pcb drc --format json --exit-code-violations` (exit 5 khi có vi phạm); `--schematic-parity` kiểm schematic khớp layout | có | [KiCad 9 CLI](https://docs.kicad.org/9.0/en/cli/cli.html), [KiCad 10 CLI](https://docs.kicad.org/10.0/en/cli/cli.html) |
| Xuất gói sản xuất | `pcb export gerbers/drill/pos/ipc2581/ipcd356/odb/step`, `sch export bom/netlist`; `jobset run` (từ KiCad 9) khai cả chuỗi xuất trong một file có phiên bản | sinh file | như trên |
| Biến thể lắp ráp | design variants (KiCad 10), `--variant` khi xuất | sinh file | [KiCad 10.0.0](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/) |
| Chuỗi CI | KiBot 1.9.1 (preflight ERC/DRC làm hỏng lần chạy; hỗ trợ KiCad 10 chưa đủ), GitHub Action `kicad-action` | có | [KiBot](https://kibot.readthedocs.io/en/latest/Changelog.html), [kicad-action](https://github.com/sparkengineering/kicad-action) |
| Ghép panel, gói cho nhà máy | KiKit `panelize`, `fab jlcpcb/pcbway` | sinh file | [KiKit](https://yaqwsx.github.io/KiKit/latest/fabrication/jlcpcb/) |
| Diff trực quan giữa hai commit | KiRI, CADLAB | cho người review | [KiRI](https://github.com/leoheck/kiri) |
| Review trên nền git | AllSpice Hub (Actions, AI reviewer) | một phần | [AllSpice](https://learn.allspice.io/drcy-ai-design-review) |
| Mô phỏng SPICE | xuất netlist bằng kicad-cli, chạy `ngspice -b` riêng | có (theo ngưỡng) | [spicelib](https://spicelib.readthedocs.io/en/latest/classes/ngspice_simulator.html) |
| Sụt áp PDN | KiPI, padne (thử nghiệm) | chỉ tham khảo | [KiPI](https://github.com/drewsum/KiPI/wiki), [padne](https://forum.kicad.info/t/presenting-padne-a-tool-for-dc-power-delivery-network-analysis/64966) |
| Trở kháng, S-parameter | gerber2ems + openEMS (chậm) | chỉ tham khảo | [gerber2ems](https://github.com/antmicro/gerber2ems) |
| Độ rộng đường mạch IPC-2152 | không thấy thư viện được bảo trì; tự viết công thức xấp xỉ | có | **[chưa kiểm]** |
| Luật DFM nhà máy | file `.kicad_dru` cộng đồng cho JLCPCB, PCBWay; chậm hơn trang năng lực thật, phải ghim phiên bản | có | [kicad-druid](https://github.com/Cimos/KiCad-CustomDesignRules) |
| Tồn kho, giá, vòng đời | DigiKey API v4 (mặc định 1.000 lần/ngày, có `ProductStatus`), Nexar/Octopart (bản miễn phí giới hạn 1.000 linh kiện trọn đời), Mouser, jlcparts (dữ liệu JLCPCB cập nhật vài giờ một lần) | có (theo ngưỡng) | [DigiKey](https://developer.digikey.com/documentation), [Nexar](https://support.nexar.com/support/solutions/articles/101000476314), [jlcparts](https://gittrend.io/repo/yaqwsx/jlcparts) |

Hai giới hạn quan trọng:

- API Python cũ (SWIG `pcbnew`) bị bỏ từ 9.0, dự kiến gỡ ở 11.0. API IPC thay thế cần pcbnew đang chạy giao diện, chưa có chế độ headless và chưa phủ schematic ([KiCad dev docs](https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/), [adamws](https://adamws.github.io/using-the-new-kicad-ipc-api-in-a-ci-environment)). Vì vậy cổng kiểm nên dựng trên `kicad-cli` và đọc trực tiếp file S-expression.
- Câu hỏi kỹ thuật của nhà máy (EQ) và xác nhận file sản xuất đi qua email, không có API: nhà máy dựng lại file, gửi ảnh đánh dấu, chờ trả lời; trả lời chậm thì giao hàng chậm ([JLCPCB](https://jlcpcb.com/help/article/how-to-confirm-the-production-file), [PCBWay](https://www.pcbway.com/helpcenter/design_service_ordering/How_Engineer_Questions_Response_Delays_Impact_Design_Lead_Time.html)).

## 3. AI trong thiết kế PCB: làm được gì, hỏng ở đâu

### 3.1. Công cụ hiện có

Gần như mọi số liệu dưới đây do chính nhà bán công bố; chưa thấy đánh giá độc lập.

- **LLM làm phần đầu** (yêu cầu, chọn linh kiện, schematic): Flux Copilot tự nêu lỗi hay gặp là sai ánh xạ chân, sai giá trị mặc định, làm dở thao tác nhiều bước, và khuyên mỗi lần chỉ giao 2–3 linh kiện ([Flux](https://unified.flux.ai/p/blog/flux-copilot-under-the-hood)); Celus và Circuit Mind đi từ sơ đồ khối ra schematic và BOM, có người giám sát ([Celus](https://celus.io/en/design-platform), [Electromaker](https://www.electromaker.io/blog/article/circuit-mind-turns-block-diagrams-into-schematics-fast)).
- **Layout do bộ tối ưu chuyên dụng làm, không phải LLM**: Quilter (dựa trên vật lý, không phải LLM) vẫn cần 38,5 giờ người dọn trên board i.MX 8M Mini 8 lớp, và tự nói không thay được kỹ sư layout ([Quilter](https://www.quilter.ai/blog/quilter-vs-cadence-allegro-x-ai)); DeepPCB dùng học tăng cường ([InstaDeep](https://instadeep.com/?p=3966)); Allegro X AI vẫn cần review và dọn **[nguồn đối thủ]**.
- **Định dạng hợp với agent**: thiết kế dạng code (atopile có MCP server, SKiDL, tscircuit) hợp hơn sửa thẳng file KiCad. File schematic thô "dài dòng, nặng hình học" ([SchGen](https://arxiv.org/abs/2605.30345)); một schematic Gemini sinh ra không mở được trong eeschema ([KiCad forum](https://forum.kicad.info/t/gemini-created-me-a-schematic-file-that-isnt/71475)). Có MCP server cho KiCad nhưng tự ghi "không thay review của kỹ sư" ([KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server)).

### 3.2. Bằng chứng về lỗi

- HWE-Bench (2026, 300 bài cấp board, 2.914 datasheet): qua luật tĩnh trung bình 71,8%, qua mô phỏng 58,7%, thiết kế đúng hoàn toàn tốt nhất chỉ 8,15%. Lỗi điển hình: bỏ sót chân GND lặp, xung đột pin-mux, gắn nhãn sai vai trò chân, mất ngữ cảnh ở IC hàng trăm chân ([arXiv 2603.18102](https://arxiv.org/html/2603.18102v1)).
- Mô hình đa phương thức đọc sai hình học bản vẽ package ([arXiv 2508.03725](https://arxiv.org/abs/2508.03725)).
- Sự cố thật: bản tóm tắt datasheet qua công cụ fetch đảo nguồn và GND, cảm biến cháy, mô hình trình bày như sự thật đã kiểm ([báo lỗi](https://claudeissues.com/issue/61504-bug-model-presents-incorrect-hardware-parameters-from-training-data-fails-to-sel)).
- Footprint của thư viện bên thứ ba (SnapMagic, Ultra Librarian, SamacSys) có quy trình kiểm nhưng không công bố tỉ lệ lỗi, và vẫn có lỗi được báo ([TI E2E](https://e2e.ti.com/support/amplifiers-group/amplifiers/f/amplifiers-forum/842303/opa541-is-the-footprint-correct)).
- Chưa thấy nghiên cứu hệ thống về tỉ lệ LLM bịa mã linh kiện (MPN); bằng chứng chỉ là giai thoại.

### 3.3. Quy tắc rút ra cho agent

Các quy tắc này vào checklist của domain pack ([README §Quy tắc cho agent](README.md#quy-tắc-cho-agent)).

## 4. Hệ quả cho kiến trúc của gói

| Phát hiện | Thay đổi trong gói |
| --- | --- |
| Placement là cổng riêng ở nơi làm bài bản (§1.2) | Sơ đồ 02 tách layout thành placement → duyệt placement → routing |
| Kiểm BOM hai lần (§1.6) | Bước kiểm BOM lặp lại trong gói gửi sản xuất, trả BLOCKED khi hết hàng |
| Gói sản xuất phải khớp nhau và khớp nguồn (§1.3) | Sơ đồ 04 chuỗi dẫn xuất, kiểm "đầu ra cũ hơn nguồn" bằng parity và hash (xử lý P5 của [thử giấy](../../docs/paper-tests/doc-types-pcb.md)) |
| Bring-up gắn với từng board, rework có nhật ký (§1.4) | Sơ đồ 03 vòng đời rev; serial board là khoá của bằng chứng (P7) |
| EQ của nhà máy qua email, có thể kéo dài giao hàng (§2) | Trạng thái "chờ EQ" trong sơ đồ 03 |
| API Python không headless (§2) | Cổng dựng trên `kicad-cli` + đọc S-expression |
| LLM sai nhiều nhất ở ánh xạ chân và hình học footprint (§3.2) | Footprint chỉ sinh bằng bộ sinh IPC-7351 từ bảng kích thước có trích trang; kiểm pin map từng chân |
