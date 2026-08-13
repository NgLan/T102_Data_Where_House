# **REQUIREMENTS**

# **PART I — PROJECT & BUSINESS**

## **0\. Document Control**

Phần này chứa các thông tin quản lý tài liệu. Mục đích là đảm bảo tài liệu có thể được xác định, theo dõi phiên bản, người chịu trách nhiệm và lịch sử cập nhật một cách rõ ràng. 

### **0.1 Document Information**

* Document Name: Master Requirements & Engineering Specification   
* Project Name: AI Agent gợi ý và thiết kế mô hình dữ liệu  
* Document Version: 0.1.0  
  * Dùng để theo dõi sự thay đổi của tài liệu theo thời gian.  
  * **Quy ước:** MAJOR.MINOR.PATCH  
    * Trong đó:  
      * **MAJOR**: Có thay đổi lớn về phạm vi, kiến trúc hoặc các quy định nền tảng của hệ thống.  
      * **MINOR**: Thêm mới hoặc thay đổi đáng kể một nhóm yêu cầu nhưng không phá vỡ các quy định hiện tại.  
      * **PATCH**: Sửa lỗi, làm rõ nội dung, chỉnh sửa câu chữ hoặc cập nhật nhỏ.  
    * **Ví dụ:** 1.0.0, 1.1.0, 1.1.1, 2.0.0  
* Status: Draft  
  * Cho biết mức độ hoàn thiện và hiệu lực hiện tại của tài liệu.   
  * Các trạng thái được sử dụng: 

| Status | Ý nghĩa |
| ----- | ----- |
| **Draft** | Đang xây dựng, nội dung chưa được thống nhất |
| **Review** | Đã có bản tương đối hoàn chỉnh và đang được review |
| **Approved** | Đã được thống nhất và có thể sử dụng làm căn cứ phát triển |
| **Deprecated** | Không còn được sử dụng |
| **Archived** | Được lưu trữ để tham khảo, không còn là tài liệu hiện hành |

* Created Date: 04/08/2026  
* Last Updated: 04/08/2026  
* Owner: Nguyễn Ngọc Lan  
* Contributors:   
  * Nguyễn Ngọc Lan  
  * Hoàng Hương Giang  
  * Vũ Hải Nam  
  * Giáp Quốc Anh

### **0.2 Document Status & Change History**

#### ***Version History*** 

| Version  | Date  | Author | Change Summary | Status |
| :---: | :---: | :---: | ----- | :---: |
| 0.1.0 | 4/8/2026 | Nguyễn Ngọc Lan | Khởi tạo document skeleton  | Draft  |

#### ***Change Rules***

* Mỗi thay đổi quan trọng phải cập nhật Document Version.

* Last Updated phải được cập nhật khi tài liệu thay đổi.

* Thay đổi requirement quan trọng phải được ghi lại trong Version History.

* Không xóa lịch sử phiên bản cũ.

* Khi một requirement bị thay đổi hoặc loại bỏ, phải ghi rõ lý do nếu thay đổi đó có ảnh hưởng đến hệ thống.

### **0.3 Document Purpose**

Tài liệu này là tài liệu yêu cầu và quy định tổng thể của dự án, được sử dụng làm **nguồn thông tin chính (Single Source of Truth)** cho việc phân tích, thiết kế, phát triển, kiểm thử, triển khai và bảo trì hệ thống.

Tài liệu có các mục đích chính:

* Mô tả hệ thống cần xây dựng và phạm vi của hệ thống.  
* Mô tả các nghiệp vụ và yêu cầu chức năng.  
* Mô tả kiến trúc và các nguyên tắc thiết kế hệ thống.  
* Xác định các yêu cầu đối với AI Agent và Multi-Agent Architecture.  
* Xác định các quy tắc thiết kế Data Warehouse.  
* Xác định quy định về Database, API và Frontend.  
* Xác định các tiêu chuẩn lập trình và cấu trúc source code.  
* Xác định các yêu cầu về Security, Testing, Logging và Performance.  
* Xác định quy trình phát triển và quản lý source code bằng Git.  
* Cung cấp các quy tắc và giới hạn mà AI coding agent phải tuân thủ khi thực hiện hoặc thay đổi code.  
* Làm cơ sở để đánh giá xem một tính năng hoặc thay đổi đã đáp ứng đầy đủ yêu cầu của hệ thống hay chưa.

**Nguyên tắc quan trọng**

Trong trường hợp có sự khác biệt giữa implementation hiện tại và requirement đã được phê duyệt trong tài liệu này, **requirement được ưu tiên làm cơ sở để đánh giá tính đúng đắn của hệ thống**.

Tuy nhiên, AI coding agent **không được tự ý thay đổi các requirement** để phù hợp với implementation hiện tại. Nếu phát hiện requirement không rõ ràng, mâu thuẫn hoặc không khả thi, agent phải tuân theo quy định tại phần **AI Decision-Making Rules** và yêu cầu con người xác nhận khi cần thiết.

### **0.4 Document Scope**

#### ***In Scope***

Tài liệu bao gồm các nhóm nội dung sau:

**Business**

* Bối cảnh và mục tiêu nghiệp vụ.  
* Các actor.  
* Business process.  
* Business rules.  
* Business requirements.  
* Các use case và business scenario.

**Product / System**

* Phạm vi chức năng của hệ thống.  
* System workflow.  
* Functional requirements.  
* Non-functional requirements.  
* System constraints.  
* System behavior.

**AI Agent**

* Multi-Agent Architecture.  
* Agent responsibilities.  
* Agent communication.  
* Agent workflow.  
* ReAct Pattern.  
* Plan-and-Execute Pattern.  
* Tool usage.  
* Agent input/output.  
* Agent validation.  
* Agent error handling.  
* Human-in-the-loop.

**Data Warehouse**

* Data Warehouse architecture.  
* Fact / Dimension design.  
* Grain.  
* Measures.  
* Relationships.  
* Surrogate keys.  
* Slowly Changing Dimensions.  
* Source-to-target mapping.  
* Data lineage.  
* Các quy tắc thiết kế Data Warehouse.

**Technical**

* System architecture.  
* Backend.  
* Frontend.  
* Database.  
* API.  
* Security.  
* Testing.  
* Logging.  
* Monitoring.  
* Performance.  
* Deployment.

**Engineering**

* Coding standards.  
* Project structure.  
* Naming conventions.  
* Git workflow.  
* Branching strategy.  
* Commit conventions.  
* Pull Request rules.  
* Code review.  
* CI/CD.  
* Documentation.

**AI Coding Agent**

* Quy tắc để AI coding agent đọc và sử dụng requirement.  
* Quyền hạn của AI agent.  
* Các hành động AI được phép tự thực hiện.  
* Các hành động AI phải yêu cầu con người xác nhận.  
* Cách xử lý requirement chưa rõ hoặc mâu thuẫn.  
* Các hành vi bị cấm.

#### ***Out of Scope***

Những nội dung không được quy định trong tài liệu này hoặc chưa được xác định sẽ được đánh dấu rõ ràng bằng **TBD**, **TODO** hoặc được chuyển sang tài liệu chuyên biệt nếu cần.

Tài liệu này **không thay thế** các tài liệu chuyên môn có yêu cầu chi tiết hơn trong tương lai, ví dụ:

* API Reference chi tiết.  
* Database Schema Reference.  
* UI/UX Design Specification.  
* Deployment Runbook.  
* User Manual.  
* Operational Manual.

Trong trường hợp các tài liệu chuyên biệt được tạo sau này, các tài liệu đó phải tham chiếu đến Master Requirements này và không được tự ý tạo ra quy định mâu thuẫn với các requirement đã được phê duyệt.

### **0.5 Intended Audience**

Tài liệu được sử dụng bởi tất cả các bên tham gia vào quá trình xây dựng và vận hành hệ thống. 

**Project Manager / Team Leader**

Sử dụng tài liệu để:

* Hiểu phạm vi dự án.  
* Theo dõi yêu cầu.  
* Theo dõi các constraint.  
* Kiểm soát thay đổi.  
* Xác định acceptance criteria.

**Business / Domain Analyst**

Sử dụng tài liệu để:

* Mô tả nghiệp vụ.  
* Xác định business rules.  
* Xác định business requirements.  
* Xác định KPI và business scenarios.

**Solution / System Architect**

Sử dụng tài liệu để:

* Thiết kế architecture.  
* Xác định system components.  
* Đưa ra architectural decisions.  
* Đảm bảo hệ thống tuân thủ các architectural constraints.

**Backend Developer**

Sử dụng tài liệu để:

* Implement backend.  
* Xây dựng API.  
* Implement business logic.  
* Implement AI Agent.  
* Tuân thủ coding standards và backend architecture.

**Frontend Developer**

Sử dụng tài liệu để:

* Implement UI/UX.  
* Xây dựng frontend architecture.  
* Tích hợp API.  
* Implement các giao diện tương tác với AI Agent.

**Data Engineer / Database Developer**

Sử dụng tài liệu để:

* Thiết kế application database.  
* Thiết kế Data Warehouse.  
* Implement data processing.  
* Tuân thủ database và DW design rules.

**AI / ML Engineer**

Sử dụng tài liệu để:

* Thiết kế Agent.  
* Implement ReAct.  
* Implement Plan-and-Execute.  
* Thiết kế Agent tools.  
* Đánh giá chất lượng Agent.

**QA / Tester**

Sử dụng tài liệu để:

* Xây dựng test cases.  
* Xác định expected behavior.  
* Kiểm tra acceptance criteria.  
* Đánh giá hệ thống có đáp ứng requirement hay không.

**DevOps / Infrastructure**

Sử dụng tài liệu để:

* Thiết lập môi trường.  
* CI/CD.  
* Deployment.  
* Monitoring.  
* Logging.  
* Infrastructure.

**AI Coding Agent**

Bao gồm nhưng không giới hạn ở:

* Codex  
* Claude Code  
* Các AI coding agent khác

AI coding agent sử dụng tài liệu này làm nguồn tham chiếu chính để hiểu yêu cầu, constraint và quy tắc phát triển của hệ thống. 

AI coding agent phải tuân thủ các quy định trong tài liệu này trong phạm vi quyền hạn được cấp. 

### **0.6 How to Use This Document**

Tài liệu này phải được sử dụng như **nguồn tham chiếu chính trong quá trình phát triển hệ thống**. 

#### ***0.6.1 General Rule***

Trước khi thực hiện một thay đổi có ảnh hưởng đến hệ thống, developer hoặc AI coding agent phải xác định các requirement và quy định liên quan trong tài liệu này.

Ví dụ: 

Thay đổi Database

        ↓

Kiểm tra Database Requirements

        ↓

Kiểm tra Data Model Rules

        ↓

Kiểm tra Naming Convention

        ↓

Kiểm tra Migration Rules

        ↓

Thực hiện thay đổi

#### ***0.6.2 Requirement Priority***

Khi có nhiều requirement liên quan đến một implementation, phải tuân thủ theo mức độ ưu tiên được định nghĩa tại **0.7 Requirement Priority Convention**.

#### ***0.6.3 Before Development***

Trước khi bắt đầu một feature mới, cần xác định:

* Feature thuộc requirement nào.  
* Business rule liên quan.  
* API requirement liên quan.  
* Database requirement liên quan.  
* UI requirement liên quan.  
* Security requirement liên quan.  
* Testing requirement liên quan.

#### ***0.6.4 Before Changing Existing Code***

Không được mặc định rằng code hiện tại là đúng.

Trước khi thay đổi code quan trọng, cần kiểm tra:

1. Requirement tương ứng.  
2. Architecture hiện tại.  
3. Các dependency liên quan.  
4. API contract.  
5. Database schema.  
6. Các test hiện có.  
7. Các constraint liên quan.

#### ***0.6.5 When Requirement Is Missing***

Nếu requirement cần thiết chưa được định nghĩa:

> **Không được tự ý tạo ra một business rule hoặc architectural rule quan trọng nếu quyết định đó có thể ảnh hưởng đến hệ thống.**

AI coding agent có thể đưa ra đề xuất, nhưng phải đánh dấu rõ hoặc yêu cầu người dùng xác nhận tùy mức độ ảnh hưởng.

#### ***0.6.6 When Requirements Conflict***

Nếu hai requirement mâu thuẫn nhau:

1. Không tự ý chọn một requirement.  
2. Xác định rõ các requirement đang xung đột.  
3. Đánh giá phạm vi ảnh hưởng.  
4. Báo cáo conflict.  
5. Yêu cầu người có thẩm quyền đưa ra quyết định.  
6. Cập nhật tài liệu sau khi quyết định được thống nhất.

#### ***0.6.7 Document Maintenance***

Khi một thay đổi trong hệ thống làm thay đổi requirement hoặc quy định:

Requirement Change

        ↓

Update Master Requirements

        ↓

Review

        ↓

Approve

        ↓

Implement

Không nên để implementation thay đổi trước rồi mới cập nhật requirement sau, trừ trường hợp emergency change được quy định riêng.

### **0.7 Requirement Priority Convention**

Để tránh việc requirement bị hiểu theo nhiều cách khác nhau, tài liệu sử dụng các từ khóa chuẩn để thể hiện **mức độ bắt buộc**.

Các từ khóa này áp dụng cho cả con người và AI coding agent.

* MUST: nghĩa là **bắt buộc phải thực hiện**.

  * Requirement sử dụng MUST không được bỏ qua hoặc thay đổi nếu chưa có sự phê duyệt tương ứng.

  * **Ví dụ:**  
    * API MUST validate tất cả dữ liệu đầu vào trước khi xử lý.  
    * Điều này có nghĩa là implementation bắt buộc phải có validation.  
* MUST NOT: nghĩa là **tuyệt đối không được thực hiện**.  
  * Thường được sử dụng cho:  
    * Security rules.  
    * Architecture constraints.  
    * Coding restrictions.  
    * Git restrictions.  
    * Các hành vi có thể gây lỗi hoặc gây nguy hiểm cho hệ thống.  
  * **Ví dụ:** AI coding agent MUST NOT commit secret hoặc API key vào repository.  
* SHOULD: nghĩa là **nên thực hiện**.   
  * Đây là requirement được khuyến nghị nhưng có thể có ngoại lệ nếu có lý do kỹ thuật hợp lý.

  * Nếu không tuân thủ SHOULD, developer phải đảm bảo rằng quyết định đó không gây ảnh hưởng tiêu cực và nên ghi nhận lý do khi cần thiết.

  * **Ví dụ:** API SHOULD sử dụng pagination đối với các endpoint trả về danh sách lớn.  
* SHOULD NOT: nghĩa là **không nên thực hiện**, nhưng có thể có ngoại lệ nếu có lý do hợp lý.  
  * **Ví dụ:** Application SHOULD NOT thực hiện các truy vấn database không có giới hạn số lượng bản ghi đối với dữ liệu lớn.  
* MAY: nghĩa là **được phép thực hiện nhưng không bắt buộc**.  
  * Dùng cho các tính năng hoặc implementation tùy chọn.  
  * **Ví dụ:**  
    * Hệ thống MAY hỗ trợ Dark Mode (Nếu không implement Dark Mode thì hệ thống vẫn đáp ứng requirement bắt buộc).

**Priority Summary**

| Keyword | Ý nghĩa | Có được bỏ qua? |
| ----- | ----- | ----- |
| **MUST** | Bắt buộc phải thực hiện | ❌ Không |
| **MUST NOT** | Tuyệt đối không được thực hiện | ❌ Không |
| **SHOULD** | Nên thực hiện | ⚠️ Có thể, nếu có lý do |
| **SHOULD NOT** | Không nên thực hiện | ⚠️ Có thể, nếu có lý do |
| **MAY** | Có thể thực hiện | ✅ Có |

### **0.8 Requirement ID Convention**

Mỗi requirement chính thức phải có một **Requirement ID duy nhất**.

Requirement ID được sử dụng để:

* Tham chiếu requirement giữa các tài liệu.  
* Liên kết requirement với implementation.  
* Liên kết requirement với test case.  
* Theo dõi requirement trong issue / Pull Request.  
* Theo dõi thay đổi requirement.  
* Giúp AI coding agent xác định chính xác requirement cần thực hiện.

#### ***0.8.1 ID Format***

Định dạng chung: \<PREFIX\>-\<NUMBER\>

Ví dụ:

FR-001

FR-002

NFR-001

DB-001

API-001

**NUMBER** sử dụng số nguyên dương, bắt đầu từ **001**. 

#### ***0.8.2 Requirement Categories*** 

| Prefix | Category | Ý nghĩa |
| ----- | ----- | ----- |
| `FR` | Functional Requirement | Yêu cầu chức năng |
| `NFR` | Non-Functional Requirement | Yêu cầu phi chức năng |
| `DB` | Database Requirement | Yêu cầu liên quan Database |
| `DW` | Data Warehouse Requirement | Yêu cầu liên quan Data Warehouse |
| `API` | API Requirement | Yêu cầu liên quan API |
| `UI` | UI Requirement | Yêu cầu giao diện |
| `AI` | AI / Agent Requirement | Yêu cầu liên quan AI Agent |
| `SEC` | Security Requirement | Yêu cầu bảo mật |
| `DEV` | Development Requirement | Quy định phát triển / coding |
| `GIT` | Git Requirement | Quy định Git |
| `TEST` | Testing Requirement | Yêu cầu kiểm thử |
| `DEP` | Deployment Requirement | Yêu cầu triển khai |
| `OPS` | Operations Requirement | Yêu cầu vận hành |
| `DOC` | Documentation Requirement | Yêu cầu tài liệu |

#### ***0.8.3 Requirement Example***

Ví dụ:

> **FR-001 — Create Project**

> Hệ thống MUST cho phép người dùng tạo một project mới.

Hoặc:

> **DB-003 — Primary Key**

> Mỗi bảng MUST có một primary key phù hợp với mục đích của bảng.

Hoặc:

> **AI-005 — Agent Tool Permission**

> AI Agent MUST NOT gọi tool nằm ngoài danh sách tool được cấp quyền.

Hoặc:

> **GIT-004 — Protected Branch**

> Developer MUST NOT push trực tiếp vào branch main.

#### ***0.8.4 Requirement ID Rules***

* Mỗi Requirement ID phải **duy nhất trong toàn bộ project**.  
* Không tái sử dụng ID của requirement đã bị xóa.  
* Khi requirement thay đổi nội dung nhưng vẫn giữ nguyên ý nghĩa, có thể giữ ID.  
* Khi requirement thay đổi bản chất, cần cân nhắc tạo Requirement ID mới.  
* Requirement ID không được thay đổi tùy tiện sau khi requirement đã được sử dụng trong issue, code hoặc test case.  
* Requirement ID phải được sử dụng khi tham chiếu đến requirement trong các tài liệu khác.

#### ***0.8.5 Requirement Traceability***

Khi hệ thống phát triển, requirement có thể được liên kết theo chuỗi:

Requirement

    ↓

Issue / Task

    ↓

Branch

    ↓

Pull Request

    ↓

Code

    ↓

Test Case

    ↓

Test Result

**Ví dụ:**

FR-015

   ↓

Issue \#42

   ↓

feature/FR-015-project-creation

   ↓

PR \#57

   ↓

Test Case TC-015

Điều này giúp team và AI coding agent có thể truy ngược: **Tại sao code này tồn tại?** và **Code này đang phục vụ requirement nào?**

## **1\. Project Overview**

### **1.1 Project Background**

Hiện nay, doanh nghiệp có thể sở hữu nhiều nguồn dữ liệu khác nhau như cơ sở dữ liệu nghiệp vụ, hệ thống giao dịch, file dữ liệu, API và các hệ thống chuyên môn. Các nguồn dữ liệu này thường có cấu trúc, cách đặt tên, mức độ chi tiết và quy tắc nghiệp vụ khác nhau.

Việc xây dựng Data Warehouse từ các nguồn dữ liệu này đòi hỏi phải thực hiện nhiều bước phân tích và thiết kế, bao gồm:

* Phân tích yêu cầu nghiệp vụ.  
* Xác định các quy trình nghiệp vụ cần phân tích.  
* Xác định các chỉ số và KPI.  
* Phân tích nguồn dữ liệu.  
* Xác định dữ liệu cần thiết cho từng nghiệp vụ.  
* Xác định grain của Fact Table.  
* Xác định Fact và Dimension.  
* Xác định mối quan hệ giữa các bảng.  
* Xác định cách xử lý dữ liệu lịch sử.  
* Xác định mapping giữa dữ liệu nguồn và Data Warehouse.  
* Kiểm tra tính hợp lý và nhất quán của mô hình.

Các công việc trên thường yêu cầu nhiều kiến thức đồng thời về nghiệp vụ, Data Modeling, Database và Data Warehouse. Quá trình thiết kế thủ công cũng có thể mất nhiều thời gian và dễ xảy ra sai sót khi số lượng nguồn dữ liệu, bảng và yêu cầu nghiệp vụ tăng lên.

Dự án này hướng tới việc xây dựng một hệ thống sử dụng **AI Agent và Multi-Agent Architecture** để hỗ trợ tự động hóa và chuẩn hóa quá trình phân tích, thiết kế Data Warehouse.

Hệ thống sẽ kết hợp nhiều Agent có trách nhiệm khác nhau. Tùy thuộc vào loại nhiệm vụ, Agent có thể sử dụng các pattern như **ReAct** hoặc **Plan-and-Execute**. Các Agent có thể phối hợp với nhau để phân tích đầu vào, thực hiện các bước thiết kế, kiểm tra kết quả và tạo ra mô hình Data Warehouse phù hợp với yêu cầu.

### **1.2 Problem Statement**

Hệ thống cần giải quyết bài toán:

> **Làm thế nào để sử dụng AI Agent nhằm hỗ trợ tự động hóa quá trình từ yêu cầu nghiệp vụ và dữ liệu nguồn đến thiết kế Data Warehouse một cách có cấu trúc, có thể kiểm tra, có khả năng giải thích và tuân thủ các quy tắc thiết kế đã được xác định?**

Các vấn đề chính cần giải quyết bao gồm:

#### ***1\. Phân tích yêu cầu nghiệp vụ***

Yêu cầu nghiệp vụ thường được mô tả dưới dạng ngôn ngữ tự nhiên và có thể không trực tiếp chỉ ra:

* Fact nào cần tạo.  
* Dimension nào cần tạo.  
* Grain của Fact là gì.  
* Measure nào cần tính.  
* Dữ liệu nào từ nguồn được sử dụng.  
* Quan hệ giữa các thực thể.

Hệ thống cần hỗ trợ chuyển đổi yêu cầu nghiệp vụ thành các thông tin có cấu trúc phục vụ quá trình thiết kế Data Warehouse.

#### ***2\. Phân tích dữ liệu nguồn***

Một hệ thống có thể có nhiều bảng nguồn với cấu trúc và ý nghĩa khác nhau.

Hệ thống cần hỗ trợ phân tích:

* Schema.  
* Table.  
* Column.  
* Data type.  
* Relationship.  
* Metadata.  
* Business meaning.  
* Các dữ liệu liên quan đến yêu cầu nghiệp vụ.

#### ***3\. Thiết kế Data Warehouse***

Từ yêu cầu nghiệp vụ và dữ liệu nguồn, hệ thống cần hỗ trợ xác định:

* Fact Table.  
* Dimension Table.  
* Grain.  
* Measure.  
* Key.  
* Relationship.  
* Historical data handling.  
* Source-to-target mapping.

#### ***4\. Kiểm tra chất lượng thiết kế***

Kết quả do AI tạo ra có thể chứa:

* Thiếu Dimension.  
* Sai Grain.  
* Sai Relationship.  
* Measure không phù hợp.  
* Không có nguồn dữ liệu tương ứng.  
* Vi phạm quy tắc thiết kế Data Warehouse.  
* Mâu thuẫn giữa các thành phần của mô hình.

Do đó, hệ thống cần có cơ chế kiểm tra và đánh giá kết quả trước khi xem đó là một thiết kế hợp lệ.

#### ***5\. Điều phối nhiều AI Agent***

Một nhiệm vụ thiết kế Data Warehouse có thể bao gồm nhiều loại công việc khác nhau.

Việc sử dụng một Agent duy nhất cho toàn bộ quy trình có thể khiến trách nhiệm của Agent quá lớn và khó kiểm soát.

Hệ thống cần có cơ chế phân chia nhiệm vụ cho nhiều Agent chuyên trách và điều phối quá trình thực hiện.

### **1.3 Project Vision**

Xây dựng một hệ thống **AI-powered Data Warehouse Design Platform** có khả năng hỗ trợ người dùng chuyển đổi từ yêu cầu nghiệp vụ và dữ liệu nguồn thành một thiết kế Data Warehouse có cấu trúc, có thể kiểm tra và có thể tiếp tục sử dụng trong quá trình phát triển hệ thống dữ liệu.

Hệ thống hướng tới mô hình:

Business Requirements \+ Source Data / Schema \+ Business Rules

↓

AI Agent System

↓

Analysis

↓

Planning

↓

Data Warehouse Design

↓

Validation / Critique

↓

Human Review

↓

Approved Data Warehouse Model

↓

ERD / DDL / Documentation

Vision của hệ thống không phải là thay thế hoàn toàn Data Engineer hoặc Business Analyst.

Thay vào đó, hệ thống đóng vai trò là **AI-assisted design system**, trong đó AI thực hiện các công việc phân tích và đề xuất, còn con người có khả năng kiểm tra, điều chỉnh và phê duyệt kết quả.

### **1.4 Project Objectives**

Dự án có các mục tiêu chính sau:

#### ***1.4.1 Tự động hóa quá trình phân tích***

Hỗ trợ tự động phân tích yêu cầu nghiệp vụ, dữ liệu nguồn và các quy tắc liên quan để giảm các công việc phân tích thủ công.

#### ***1.4.2 Hỗ trợ thiết kế Data Warehouse***

Hỗ trợ tạo đề xuất Data Warehouse Model bao gồm:

* Fact.  
* Dimension.  
* Grain.  
* Measure.  
* Key.  
* Relationship.  
* Các thuộc tính cần thiết.  
* Source-to-target mapping.

#### ***1.4.3 Sử dụng Multi-Agent Architecture***

Phân chia quá trình xử lý thành các Agent có trách nhiệm chuyên biệt thay vì giao toàn bộ nhiệm vụ cho một Agent duy nhất.

#### ***1.4.4 Kết hợp nhiều Agent Pattern***

Hệ thống hỗ trợ kết hợp:

* **ReAct Pattern** cho các nhiệm vụ cần quan sát kết quả, sử dụng tool và điều chỉnh hành động theo từng bước.  
* **Plan-and-Execute Pattern** cho các nhiệm vụ có thể phân rã thành nhiều bước cần lập kế hoạch trước khi thực hiện.

Việc lựa chọn pattern phải phụ thuộc vào loại nhiệm vụ và được quy định cụ thể trong phần AI Agent Architecture.

#### ***1.4.5 Kiểm tra và đánh giá kết quả***

Hệ thống phải có khả năng kiểm tra thiết kế được tạo ra dựa trên các quy tắc đã được định nghĩa.

#### ***1.4.6 Hỗ trợ Human-in-the-Loop***

Người dùng phải có khả năng:

* Xem kết quả AI.  
* Xem lý do hoặc căn cứ của đề xuất khi hệ thống hỗ trợ.  
* Chỉnh sửa kết quả.  
* Từ chối kết quả.  
* Phê duyệt kết quả.  
* Yêu cầu AI thực hiện lại hoặc điều chỉnh.

#### ***1.4.7 Chuẩn hóa quá trình phát triển***

Hệ thống và source code phải tuân thủ các quy định thống nhất về:

* Architecture.  
* Database.  
* API.  
* UI.  
* Security.  
* Testing.  
* Coding style.  
* Git.  
* Documentation.

### **1.5 Expected Outcomes**

Sau khi hoàn thành, hệ thống dự kiến cung cấp các kết quả chính sau:

#### ***1.5.1 AI Agent System***

Một hệ thống Multi-Agent có khả năng phối hợp nhiều Agent để thực hiện quá trình phân tích và thiết kế Data Warehouse.

#### ***1.5.2 Data Warehouse Design***

Hệ thống có khả năng tạo hoặc đề xuất một Data Warehouse Model dựa trên đầu vào của người dùng.

Kết quả có thể bao gồm:

* Fact Tables.  
* Dimension Tables.  
* Attributes.  
* Measures.  
* Keys.  
* Relationships.  
* Grain.  
* Mapping với dữ liệu nguồn.

#### ***1.5.3 Validation Result***

Hệ thống cung cấp kết quả kiểm tra thiết kế và chỉ ra các vấn đề được phát hiện.

**Ví dụ:**

* Missing Dimension  
* Invalid Relationship  
* Incorrect Grain  
* Missing Measure  
* Unsupported Source Mapping  
* Business Rule Violation

#### ***1.5.4 Visualization***

Người dùng có thể trực quan hóa Data Warehouse Model, ví dụ dưới dạng ERD hoặc các hình thức biểu diễn tương ứng.

#### ***1.5.5 Exportable Output***

Hệ thống có khả năng tạo ra các đầu ra phục vụ quá trình phát triển tiếp theo, ví dụ:

* Data model.  
* ERD.  
* DDL.  
* Documentation.  
* Source-to-target mapping.

Các định dạng cụ thể sẽ được xác định trong phần [**Functional Requirements**](#6.-functional-requirements).

#### ***1.5.6 Traceability***

Có khả năng truy xuất mối liên hệ giữa:

Business Requirement

↓

Business Rule / KPI

↓

Source Data

↓

DW Design

↓

Validation

↓

Generated Output

Mục tiêu là giúp người dùng hiểu được một thành phần trong Data Warehouse được tạo ra dựa trên yêu cầu hoặc dữ liệu nguồn nào.

### **1.6 Project Scope**

**Business Requirement Analysis**

Hệ thống hỗ trợ:

* Nhập yêu cầu nghiệp vụ.  
* Phân tích yêu cầu.  
* Xác định business entities.  
* Xác định business process.  
* Xác định KPI / Measure.  
* Xác định business rules liên quan.

**Source Data Analysis**

Hệ thống hỗ trợ:

* Nhập schema hoặc metadata của nguồn dữ liệu.  
* Phân tích table và column.  
* Phân tích relationship.  
* Mapping dữ liệu nguồn với yêu cầu nghiệp vụ.

**Data Warehouse Design**

Hệ thống hỗ trợ:

* Xác định Fact.  
* Xác định Dimension.  
* Xác định Grain.  
* Xác định Measure.  
* Xác định Key.  
* Xác định Relationship.  
* Đề xuất cách xử lý dữ liệu lịch sử.  
* Tạo Data Warehouse Model.

**AI Agent**

Hệ thống bao gồm:

* Multi-Agent Architecture.  
* Agent điều phối.  
* ReAct.  
* Plan-and-Execute.  
* Tool usage.  
* Agent validation.  
* Agent collaboration.  
* Agent error handling.

**Validation**

Hệ thống hỗ trợ kiểm tra:

* Tính nhất quán.  
* Tính đầy đủ.  
* Tính hợp lệ của model.  
* Tuân thủ Data Warehouse design rules.  
* Mapping giữa source và target.

**User Interface**

Hệ thống cung cấp giao diện để người dùng:

* Nhập dữ liệu.  
* Theo dõi quá trình Agent xử lý.  
* Xem kết quả.  
* Xem Data Warehouse Model.  
* Review kết quả.  
* Chỉnh sửa và phê duyệt kết quả.

### **1.7 Out of Scope**

Các nội dung sau đây **không thuộc phạm vi mặc định của phiên bản hiện tại**, trừ khi được bổ sung thành requirement chính thức.

#### ***1.7.1 Production Data Warehouse***

Hệ thống không mặc định chịu trách nhiệm xây dựng và vận hành một Data Warehouse production thực tế cho doanh nghiệp.

#### ***1.7.2 Full ETL/ELT Platform***

Hệ thống tập trung vào **phân tích và thiết kế Data Warehouse**, không mặc định trở thành một nền tảng ETL/ELT hoàn chỉnh.

#### ***1.7.3 Autonomous Production Deployment***

AI Agent không được tự động triển khai thay đổi lên production nếu chưa có requirement và cơ chế phê duyệt tương ứng.

#### ***1.7.4 Fully Autonomous Decision Making***

AI không được mặc định có quyền tự quyết đối với các quyết định quan trọng về:

* Business rule.  
* Architecture.  
* Database schema.  
* Security.  
* Production infrastructure.

#### ***1.7.5 Real Enterprise Data***

Trong quá trình phát triển và kiểm thử, không sử dụng dữ liệu doanh nghiệp thực tế hoặc dữ liệu nhạy cảm nếu chưa có cơ chế bảo mật và quyền sử dụng phù hợp.

#### ***1.7.6 Domain-Specific Production System***

Việc hệ thống được áp dụng thử nghiệm cho một domain cụ thể không có nghĩa hệ thống trở thành hệ thống nghiệp vụ production của domain đó.

Domain cụ thể sẽ được xác định tại các phần [**Business Domain**](#heading=h.bgnjxf9p42uz).

### **1.8 Success Criteria**

Dự án được xem là đạt mục tiêu khi đáp ứng các tiêu chí được thống nhất dưới đây. 

#### ***1.8.1 Functional Success***

Hệ thống có thể thực hiện đầy đủ workflow chính từ:

Input

→ Analysis

→ Planning

→ Agent Execution

→ DW Design

→ Validation

→ Human Review

→ Output

#### ***1.8.2 Data Warehouse Design Quality***

Thiết kế được tạo ra phải đáp ứng các Data Warehouse design rules đã được định nghĩa trong tài liệu.

Các tiêu chí cụ thể sẽ được xác định tại phần: [**10\. Data Warehouse Design Rules**](#12.-data-warehouse-design-rules)

#### ***1.8.3 AI Agent Quality***

AI Agent phải có khả năng:

* Hoàn thành các nhiệm vụ được giao.  
* Sử dụng đúng tool.  
* Tuân thủ giới hạn quyền hạn.  
* Phát hiện lỗi.  
* Xử lý hoặc báo cáo lỗi.  
* Không tự ý đưa ra quyết định vượt quá quyền hạn.

#### ***1.8.4 Validation Quality***

Hệ thống phải có khả năng phát hiện các lỗi hoặc vấn đề quan trọng trong Data Warehouse Design.

Các metric đánh giá cụ thể sẽ được xác định tại: **[20\. AI Evaluation](#20.-ai-evaluation)**

#### ***1.8.5 Traceability***

Các thành phần quan trọng của Data Warehouse phải có khả năng truy xuất về nguồn gốc của chúng khi hệ thống có đủ thông tin để thực hiện việc truy xuất.

#### ***1.8.6 Engineering Quality***

Source code phải đáp ứng các quy định về:

* Architecture.  
* Coding standards.  
* Testing.  
* Security.  
* Git.  
* Documentation.

#### ***1.8.7 User Acceptance***

Người dùng mục tiêu có thể sử dụng hệ thống để hoàn thành workflow chính mà không cần can thiệp thủ công vào source code của hệ thống.

### **1.9 Constraints**

Dự án được phát triển trong một số giới hạn và điều kiện nhất định.

#### ***1.9.1 Technology Constraints***

Các công nghệ được phép sử dụng phải tuân thủ Technology Stack được thống nhất trong tài liệu.

Việc thêm một framework, library hoặc infrastructure component mới phải tuân thủ quy định về dependency management.

#### ***1.9.2 AI / LLM Constraints***

Hệ thống phụ thuộc vào khả năng của LLM được sử dụng.

Kết quả từ LLM không được mặc định xem là chính xác tuyệt đối.

Các kết quả quan trọng phải được validation hoặc human review theo quy định.

#### ***1.9.3 Data Constraints***

Chất lượng của kết quả Data Warehouse phụ thuộc vào:

* Chất lượng dữ liệu nguồn.  
* Metadata.  
* Schema.  
* Business requirements.  
* Business rules.

Hệ thống không được giả định rằng dữ liệu nguồn luôn đầy đủ hoặc chính xác.

#### ***1.9.4 Development Constraints***

Mọi implementation phải tuân thủ:

* Project architecture.  
* Coding standards.  
* Git workflow.  
* Testing requirements.  
* Security requirements.

#### ***1.9.5 Security Constraints***

Không được đưa các thông tin nhạy cảm như:

* API key.  
* Password.  
* Secret.  
* Credential.

vào source code hoặc repository.

#### ***1.9.6 Human Approval Constraints***

Các hành động có ảnh hưởng lớn đến hệ thống phải tuân thủ cơ chế Human-in-the-Loop khi được quy định.

### **1.10 Assumptions**

Các assumption dưới đây được sử dụng làm cơ sở ban đầu cho quá trình thiết kế. Nếu assumption không còn đúng, requirement liên quan phải được xem xét lại.

#### ***1.10.1 Input Assumptions***

Giả định rằng người dùng có thể cung cấp một hoặc nhiều loại thông tin đầu vào như:

* Business Requirements.  
* Business Rules.  
* KPI.  
* Source Schema.  
* Data Dictionary.  
* Metadata.  
* Sample Data.

Không phải mọi loại input đều bắt buộc phải có trong mọi workflow. Requirement cụ thể sẽ xác định input tối thiểu cho từng chức năng.

#### ***1.10.2 Data Assumptions***

Giả định rằng source data có metadata đủ để hệ thống thực hiện phân tích ở mức độ cần thiết.

Nếu thông tin không đủ, hệ thống phải xác định phần thông tin còn thiếu thay vì tự động tạo ra thông tin không có căn cứ.

#### ***1.10.3 AI Assumptions***

Giả định rằng LLM có khả năng:

* Hiểu ngôn ngữ tự nhiên.  
* Phân tích schema.  
* Thực hiện reasoning theo workflow được thiết kế.  
* Sử dụng tool.  
* Tạo structured output.

Tuy nhiên, hệ thống không được dựa vào assumption rằng LLM luôn đưa ra kết quả chính xác.

#### ***1.10.4 User Assumptions***

Giả định rằng người dùng có kiến thức cơ bản về nghiệp vụ hoặc Data Warehouse đủ để review và phê duyệt kết quả AI khi cần thiết.

#### ***1.10.5 Architecture Assumptions***

Hệ thống được thiết kế theo hướng Multi-Agent và có khả năng sử dụng nhiều Agent chuyên trách.

Pattern cụ thể được sử dụng cho từng Agent sẽ được xác định trong phần [**AI Agent Architecture**](#7.-ai-agent-architecture).

### **1.11 Glossary / Terminology**

Phần này định nghĩa các thuật ngữ được sử dụng xuyên suốt tài liệu.

Các thuật ngữ có định nghĩa chính thức trong phần này phải được sử dụng thống nhất trong toàn bộ project.

#### ***AI Agent***

Một thành phần phần mềm sử dụng mô hình AI/LLM để thực hiện một nhiệm vụ cụ thể theo context, instruction, tool và quyền hạn được cung cấp.

#### ***Multi-Agent System***

Hệ thống bao gồm nhiều AI Agent có trách nhiệm khác nhau và có khả năng phối hợp để hoàn thành một nhiệm vụ lớn.

#### ***ReAct***

Pattern trong đó Agent thực hiện chu trình:

Reason / Analyze

→ Act

→ Observe

→ Re-analyze

→ ...

Agent có thể sử dụng tool, quan sát kết quả và tiếp tục quyết định hành động tiếp theo.

#### ***Plan-and-Execute***

Pattern trong đó Agent:

Plan

→ Execute Step 1

→ Execute Step 2

→ ...

→ Complete

Nhiệm vụ được phân rã thành các bước trước khi thực hiện.

#### ***Agent điều phối***

Thành phần chịu trách nhiệm điều phối quá trình thực hiện giữa các Agent.

#### ***Tool***

Một chức năng hoặc interface mà Agent được phép gọi để thực hiện một hành động cụ thể, chẳng hạn như đọc schema, truy vấn dữ liệu hoặc kiểm tra model.

#### ***Business Requirement***

Yêu cầu mô tả nhu cầu hoặc mục tiêu của nghiệp vụ mà hệ thống cần đáp ứng.

#### ***Business Rule***

Một quy tắc hoặc điều kiện nghiệp vụ mà hệ thống phải tuân thủ.

#### ***KPI***

Chỉ số được sử dụng để đo lường một khía cạnh quan trọng của hoạt động nghiệp vụ.

#### ***Data Warehouse***

Hệ thống lưu trữ dữ liệu được tổ chức nhằm phục vụ phân tích và báo cáo.

#### ***Fact Table***

Bảng lưu trữ các sự kiện hoặc hoạt động nghiệp vụ có thể được đo lường.

#### ***Dimension Table***

Bảng cung cấp ngữ cảnh mô tả cho các sự kiện được lưu trong Fact Table.

#### ***Grain***

Mức độ chi tiết được biểu diễn bởi một dòng trong Fact Table.

#### ***Measure***

Giá trị có thể được đo lường hoặc tổng hợp trong quá trình phân tích.

#### ***Source Data***

Dữ liệu được lấy từ các hệ thống hoặc nguồn dữ liệu đầu vào của quá trình thiết kế Data Warehouse.

#### ***Data Model***

Mô hình mô tả cấu trúc dữ liệu, các thực thể, thuộc tính và mối quan hệ giữa chúng.

#### ***ERD***

Entity Relationship Diagram — sơ đồ biểu diễn các entity, thuộc tính và relationship giữa chúng.

#### ***DDL***

Data Definition Language — tập hợp các câu lệnh SQL được sử dụng để định nghĩa cấu trúc database, chẳng hạn như CREATE TABLE, ALTER TABLE và CREATE INDEX.

#### ***Human-in-the-Loop***

Cơ chế trong đó con người tham gia vào một hoặc nhiều bước của quá trình AI để review, điều chỉnh, xác nhận hoặc phê duyệt kết quả.

#### ***Single Source of Truth***

Nguồn thông tin chính thức được sử dụng làm căn cứ thống nhất khi có nhiều nguồn thông tin khác nhau.

#### ***Requirement***

Một yêu cầu hoặc quy định mà hệ thống hoặc quá trình phát triển phải đáp ứng.

#### ***Functional Requirement***

Yêu cầu mô tả **hệ thống phải thực hiện chức năng gì**.

#### ***Non-Functional Requirement***

Yêu cầu mô tả **hệ thống phải hoạt động như thế nào**, chẳng hạn như performance, security, availability hoặc scalability.

#### ***AI Coding Agent***

AI Agent được sử dụng để hỗ trợ hoặc thực hiện các công việc phát triển phần mềm như phân tích requirement, viết code, sửa code, tạo test và review implementation.

## **2\. SYSTEM & BUSINESS REQUIREMENTS**

### **2.1 Mục đích**

Chương này mô tả các yêu cầu và logic nghiệp vụ cốt lõi của hệ thống AI-powered Data Warehouse Design Platform.

Khác với Chương 1 tập trung mô tả mục tiêu, phạm vi và định hướng của dự án, Chương 2 mô tả cách hệ thống phải vận hành ở mức nghiệp vụ và hành vi hệ thống, bao gồm:

* Các đối tượng nghiệp vụ chính của hệ thống.  
* Vòng đời của Project, Requirement, Agent Session và Data Model.  
* Quy trình tiếp nhận và phân tích Requirement.  
* Quy trình tiếp nhận và phân tích Source Data.  
* Quy trình Multi-Agent thực hiện phân tích và thiết kế.  
* Quy trình tạo, kiểm tra, review và phê duyệt Data Model.  
* Quy tắc Human-in-the-Loop.  
* Business Rules và System Rules.  
* State và State Transition.  
* Error Handling và Edge Cases.  
* Traceability giữa Requirement, Agent Processing, Data Model và Generated Output.

Các yêu cầu trong chương này là cơ sở để xây dựng Use Case, Functional Requirements, AI Agent Architecture, Database, API, UI/UX và Test Cases ở các chương tiếp theo.

AI Coding Agent phải sử dụng chương này để hiểu **system behavior và business logic**, nhưng không được tự suy diễn các hành vi chưa được quy định khi hành vi đó có ảnh hưởng đến architecture, database, API, security hoặc business logic.

### **2.2 System Business Model**

Hệ thống hỗ trợ người dùng chuyển đổi từ yêu cầu nghiệp vụ và dữ liệu nguồn thành một Data Warehouse Model có cấu trúc, có thể kiểm tra, review và tiếp tục sử dụng trong quá trình phát triển.

Luồng nghiệp vụ tổng quát:

User

  ↓

Project

  ↓

Business / Analytical / Technical Requirements \+ Business Rules / KPI \+ Source Data / Schema / Metadata

  ↓

AI Agent System

  ↓

Requirement Analysis

  ↓

Source Data Analysis

  ↓

Analytical Analysis

  ↓

Data Warehouse Design

  ↓

Validation / Critique

  ↓

Human Review

  ↓

Approved Data Model

  ↓

ERD / DDL / Documentation / Mapping

Hệ thống không mặc định thay thế hoàn toàn Business Analyst, Data Analyst hoặc Data Engineer. AI có nhiệm vụ phân tích, suy luận và đề xuất; con người có quyền kiểm tra, điều chỉnh và phê duyệt các kết quả quan trọng.

### **2.3 Core Business Objects**

Hệ thống sử dụng các đối tượng nghiệp vụ chính sau:

| Object | Ý nghĩa |
| ----- | ----- |
| User | Người sử dụng hệ thống |
| Project | Không gian làm việc chứa toàn bộ dữ liệu và kết quả của một bài toán |
| Project Member | Các thành viên trong một Project |
| Requirement | Yêu cầu đầu vào của người dùng |
| Analytical Requirement | Yêu cầu phân tích được Agent suy ra từ Requirement |
| Data Source | Nguồn dữ liệu đầu vào |
| Agent Session | Một phiên tương tác/xử lý của Multi-Agent |
| Session Event | Một sự kiện xảy ra trong Agent Session |
| Data Model | Data Warehouse Model hiện tại của Project |
| Data Model Change | Một thay đổi được đề xuất đối với Data Model |

Các object này phải được duy trì nhất quán giữa Business Logic, Database, API và UI.

Application Database hiện tại đã phản ánh các object chính này thông qua ***users, projects, project\_members, requirements, analytical\_requirements, data\_sources, agent\_sessions, session\_events, data\_models và data\_model\_changes.***

### **2.4 User & Project Business Logic**

#### ***2.4.1 User***

User là người sử dụng hệ thống.

Mỗi User có:

* Identity.  
* Role.  
* Status.  
* Thông tin tạo/cập nhật.

Các role hiện tại:

* ADMIN

* USER

User chỉ được thực hiện các hành động phù hợp với role của mình.

#### ***2.4.2 Project***

Project là đơn vị làm việc chính của hệ thống.

Một Project chứa các thành phần liên quan đến một bài toán Data Warehouse, bao gồm:

* Requirement.  
* Analytical Requirement.  
* Data Source.  
* Agent Session.  
* Data Model.  
* Data Model Change.

Project phải có một người tạo (created\_by) và có thể có nhiều thành viên.

Project là boundary chính để phân tách dữ liệu giữa các bài toán khác nhau.

#### ***2.4.3 Project Membership***

User có thể tham gia Project với vai trò:

* OWNER

* MEMBER

Owner có quyền quản lý Project và các thành phần thuộc Project theo Authorization Rules.

Member chỉ được thực hiện các thao tác được cấp quyền.

Một User không được truy cập hoặc thay đổi dữ liệu của Project mà User không có quyền truy cập.

### **2.5 Project Lifecycle**

Project có các trạng thái:

DRAFT

  ↓

ANALYZING

   ↓

ARCHIVED

#### ***2.5.1 ACTIVE***

Project đang hoạt động và người dùng có thể tiếp tục làm việc với Project.

Người dùng có thể:

* Chỉnh sửa thông tin Project.  
* Thêm, sửa hoặc xóa Requirement.  
* Thêm, sửa hoặc xóa Data Source.  
* Cấu hình hoặc thay đổi các input cần thiết.  
* Xem và chỉnh sửa Data Model hiện tại.  
* Trao đổi với Agent và yêu cầu thực hiện các thay đổi.

Project ở trạng thái `ACTIVE` **không có nghĩa là đã hoàn thành**. Đây là trạng thái bình thường khi Project không có workflow phân tích đang chạy.

#### ***2.5.2 ANALYZING***

Project đang có một hoặc nhiều tác vụ phân tích được Multi-Agent thực hiện.

Trong trạng thái này:

* Agent có thể thực hiện các nhiệm vụ được giao.  
* Agent có thể sử dụng Tool.  
* Agent có thể gọi Agent khác.  
* Agent có thể tạo intermediate result.  
* Agent có thể yêu cầu User cung cấp thông tin còn thiếu.  
* User vẫn có thể xem lịch sử và kết quả hiện tại.

Sau khi workflow hoàn thành hoặc bị dừng, Project quay về `ACTIVE`.

#### ***2.5.3 ARCHIVED***

Project không còn được sử dụng để làm việc thường xuyên nhưng vẫn được lưu trữ.

Trong trạng thái này:

* Người dùng có thể xem Project và các kết quả đã tạo.  
* Có thể xem Requirement, Data Source, Session và Data Model đã lưu.  
* Không thực hiện workflow Agent mới.  
* Không cho phép thay đổi dữ liệu nếu chưa khôi phục Project về `ACTIVE`.

Project có thể được **Unarchive/Restore** để tiếp tục làm việc.

### **2.6 Requirement Management Logic**

Requirement là thông tin đầu vào mô tả điều người dùng hoặc doanh nghiệp mong muốn hệ thống phân tích.

Requirement hiện tại được phân loại thành:

* BUSINESS

* ANALYTICAL

* TECHNICAL

Trong đó:

**BUSINESS**

Mô tả doanh nghiệp muốn đạt được điều gì.

Ví dụ:

> Phân tích hiệu quả hoạt động kinh doanh.

**ANALYTICAL**

Mô tả cụ thể cần phân tích dữ liệu như thế nào.

Ví dụ:

> Phân tích doanh thu theo sản phẩm và tháng.

**TECHNICAL**

Mô tả yêu cầu hoặc ràng buộc kỹ thuật.

Ví dụ:

> Các bảng dữ liệu phải có khóa chính rõ ràng và không được sử dụng khóa tự sinh làm business key.

> Dữ liệu nhạy cảm phải được ẩn danh trước khi đưa vào Data Warehouse. 

### **2.7 Requirement Processing Workflow**

Quy trình xử lý Requirement:

Requirement Intake

       ↓

Requirement Classification

       ↓

Requirement Analysis

       ↓

Information Extraction

       ↓

Missing Information Detection

       ↓

Clarification nếu cần

       ↓

Analytical Requirement

       ↓

Validation

       ↓

Approved Requirement

#### ***2.7.1 Requirement Intake***

User nhập Requirement dưới dạng text thông qua các giao diện được hệ thống hỗ trợ.

Requirement phải thuộc một Project.

#### ***2.7.2 Requirement Classification***

Hệ thống xác định Requirement thuộc loại nào:

* Business.  
* Analytical.  
* Technical.

Nếu không thể xác định chắc chắn, Agent không được tự ý gán loại khi việc gán loại có thể ảnh hưởng đến workflow.

Agent phải yêu cầu clarification hoặc đánh dấu uncertainty theo quy định của AI Agent Architecture.

#### ***2.7.3 Requirement Analysis***

Agent phân tích Requirement để xác định những thông tin liên quan, có thể bao gồm:

* Business objective.  
* Business process.  
* Business entity.  
* KPI / Measure.  
* Dimension.  
* Time dimension.  
* Business rule.  
* Analytical requirement.  
* Required source data.

#### ***2.7.4 Missing Information Detection***

Nếu Requirement không đủ thông tin để thực hiện bước tiếp theo, hệ thống phải xác định thông tin còn thiếu và hỏi người dùng để xác nhận.

Hệ thống không được tự động tạo ra thông tin không có căn cứ chỉ để hoàn thành workflow.

#### ***2.7.5 Clarification***

Agent có thể đặt câu hỏi cho User khi:

* Requirement không rõ nghĩa.  
* Có nhiều cách hiểu hợp lý.  
* Thiếu thông tin quan trọng.  
* Có mâu thuẫn giữa các Requirement.  
* Có business rule chưa xác định.  
* Không thể xác định Grain/KPI/Dimension một cách đáng tin cậy.

Khi Agent đặt câu hỏi có tính chất blocking, workflow phải tạm dừng cho đến khi User trả lời.

### **2.8 Analytical Requirement Logic**

Analytical Requirement là cấu trúc hóa yêu cầu phân tích từ Requirement ban đầu.

Một Analytical Requirement có thể bao gồm:

* Metric.  
* Dimension.  
* Time Granularity.  
* Aggregation Method.  
* Grain.

Ví dụ:

Requirement:

Phân tích doanh thu theo khoa theo tháng.

↓

Metric:

Revenue

Dimension:

Department

Time Granularity:

Month

Aggregation:

SUM

Grain:

Revenue per Department per Month

Database hiện tại đã có các trường tương ứng trong analytical\_requirements.

Agent phải phân biệt:

Requirement ≠ Analytical Requirement ≠ Data Model

Requirement mô tả nhu cầu.

Analytical Requirement mô tả nhu cầu phân tích dưới dạng có cấu trúc.

Data Model là thiết kế dữ liệu được tạo ra để đáp ứng các yêu cầu đã xác định.

### **2.9 Data Source Business Logic**

Data Source là nguồn dữ liệu được sử dụng làm cơ sở cho quá trình thiết kế.

Data Source có thể chứa:

* Schema.  
* Table.  
* Column.  
* Data Type.  
* Primary Key.  
* Foreign Key.  
* Relationship.  
* Metadata.  
* Sample Data nếu được cung cấp.

Trong MVP, Data Source ưu tiên hỗ trợ file CSV theo thiết kế hiện tại; các loại nguồn khác có thể được mở rộng theo Requirement tương ứng. Database hiện tại lưu **schema\_metadata** dưới dạng JSONB để lưu metadata được trích xuất từ source.

### **2.10 Source Data Analysis Workflow**

Data Source Input

       ↓

Source Validation

       ↓

Schema / Metadata Extraction

       ↓

Table Analysis

       ↓

Column Analysis

       ↓

Relationship Analysis

       ↓

Data Profiling nếu có

       ↓

Requirement-to-Source Mapping

       ↓

Source Analysis Result

Agent phải phân biệt:

* Thông tin có thật trong source.  
* Thông tin được suy luận.  
* Thông tin chưa xác định.

Agent không được coi một thông tin suy luận là source fact nếu không có căn cứ.

### **2.11 Business Rules, KPI & Measures** 

Business Rule là quy tắc nghiệp vụ được sử dụng làm căn cứ trong quá trình phân tích Requirement và thiết kế Data Warehouse.

KPI/Measure là các chỉ số hoặc giá trị cần được đo lường, tính toán hoặc tổng hợp để đáp ứng Analytical Requirement.

Business Rule, KPI và Measure có thể xuất hiện trong các nguồn đầu vào của hệ thống, bao gồm:

\- Được người dùng cung cấp trực tiếp.

\- Được xác định từ Business Requirement.

\- Được xác định trong quá trình Requirement Analysis.

\- Được Agent đề xuất dựa trên các thông tin đầu vào.

\- Được User review, chỉnh sửa hoặc xác nhận.

Hệ thống phải phân biệt giữa:

\- Information được User cung cấp hoặc xác nhận.

\- Information được Agent suy luận hoặc đề xuất.

\- Information chưa được xác định.

Agent không được coi một Business Rule, KPI hoặc Measure do mình suy luận là thông tin đã được User xác nhận nếu chưa có cơ chế xác nhận tương ứng.

### **2.12 Data Warehouse Design Business Logic**

Sau khi Requirement, Analytical Requirement và Source Data đã được phân tích, hệ thống thực hiện Data Warehouse Design.

Quy trình tổng quát:

Business Requirement \+ Analytical Requirement \+ Business Rules / KPI \+ Source Data

       ↓

Fact Identification

       ↓

Dimension Identification

       ↓

Grain Definition

       ↓

Measure Definition

       ↓

Key Definition

       ↓

Relationship Definition

       ↓

Historical Data Handling

       ↓

Source-to-Target Mapping

       ↓

Data Warehouse Model

Kết quả có thể bao gồm:

* Fact Tables.  
* Dimension Tables.  
* Attributes.  
* Measures.  
* Keys.  
* Relationships.  
* Grain.  
* Source-to-target mapping.

### **2.13 AI Agent Execution Logic**

Multi-Agent System thực hiện nhiệm vụ thông qua nhiều Agent chuyên trách.

Luồng tổng quát:

User Request

      ↓

Agent Session

      ↓

Supervisor

      ↓

Task Planning

      ↓

Task Decomposition

      ↓

Specialized Agents

      ↓

Agent Results

      ↓

Validation / Critique

      ↓

Result Aggregation

      ↓

Human Review

Agent không được tự ý thay đổi các dữ liệu hoặc kết quả quan trọng mà không tuân thủ Permission Boundary và Human-in-the-Loop Rules.

Chi tiết kiến trúc Agent được quy định tại Chương 5–9.

### **2.14 Agent Session Logic**

Mỗi quá trình tương tác hoặc xử lý của Agent được quản lý thông qua Agent Session.

Một Session thuộc về:

* Một Project.  
* Một User.

Session có các trạng thái:

* ACTIVE

* COMPLETED

* ARCHIVED

Trong Session, mọi hoạt động quan trọng của Agent được ghi nhận dưới dạng Session Event.

### **2.15 Session Event Logic**

Session Event được sử dụng để ghi nhận quá trình Agent và User tương tác.

Các Event Type hiện tại:

* MESSAGE

* QUESTION

* ANSWER

* AGENT\_CALL

* AGENT\_RESULT

* TOOL\_CALL

* TOOL\_RESULT

Ví dụ:

USER MESSAGE

      ↓

AGENT QUESTION

      ↓

USER ANSWER

      ↓

AGENT\_CALL

      ↓

TOOL\_CALL

      ↓

TOOL\_RESULT

      ↓

AGENT\_RESULT

Event phải được lưu theo thứ tự thời gian và phải đủ thông tin để truy xuất lại quá trình xử lý.

Thiết kế **session\_events** hiện tại đã phản ánh mô hình này.

### **2.16 Human-in-the-Loop Logic**

Human-in-the-Loop được áp dụng khi kết quả hoặc hành động của Agent cần sự kiểm tra/xác nhận của User.

User có thể:

* Xem kết quả.  
* Xem căn cứ hoặc lý do của đề xuất nếu hệ thống hỗ trợ.  
* Chỉnh sửa.  
* Accept.  
* Reject.  
* Yêu cầu Agent thực hiện lại.  
* Cung cấp thêm thông tin.

AI không được coi kết quả của chính mình là kết quả cuối cùng nếu workflow yêu cầu Human Review.

### **2.17 Data Model Lifecycle**

Data Model là phiên bản thiết kế Data Warehouse hiện tại của Project.

Data Model có:

* DBML.  
* Revision.  
* Created At.  
* Updated At.

Revision được sử dụng để kiểm soát thay đổi đồng thời.

#### ***2.17.1 User Editing***

Khi User chỉnh sửa Data Model:

Get Current DBML \+ Revision

        ↓

Edit

        ↓

Submit DBML \+ Base Revision

        ↓

Check Current Revision

Nếu revision vẫn khớp:

* Update DBML  
* Increase Revision  
* Commit

Nếu revision không khớp:

* Reject Update  
* Notify Conflict  
* Require Reload / Review

### **2.18 Data Model Change Proposal**

Agent không được trực tiếp ghi đè Data Model hiện tại khi workflow yêu cầu Human Review.

Thay vào đó Agent tạo: Data Model Change 

bao gồm:

* Data Model ID.  
* Base Revision.  
* Proposed DBML.  
* Reason.  
* Status.

Proposal ban đầu có trạng thái: PROPOSED

Thiết kế này đã được phản ánh trong **data\_model\_changes**.

### **2.19 Proposal Review Logic**

Proposal có thể chuyển trạng thái:

PROPOSED

   ├── ACCEPTED

   ├── REJECTED

   └── CONFLICTED

#### ***Accept***

Khi User Accept:

Check base\_revision

        ↓

base\_revision \== current\_revision ?

        ↓

      YES

        ↓

Apply proposed DBML

        ↓

Increase revision

        ↓

Mark ACCEPTED

Nếu revision không khớp:

Do not overwrite current DBML

        ↓

Mark CONFLICTED

        ↓

Require User Review

### **2.20 Concurrent Data Model Editing**

Hệ thống phải xử lý trường hợp nhiều User hoặc Agent cùng làm việc trên một Data Model.

#### ***Happy Case 1 — Một User chỉnh sửa***

User gửi revision hiện tại và hệ thống cập nhật thành công nếu revision vẫn hợp lệ.

#### ***Happy Case 2 — Nhiều User cùng mở nhưng chỉ một User lưu trước***

User lưu trước thành công.

User lưu sau gửi revision cũ và nhận conflict.

#### ***Happy Case 3 — Agent tạo Proposal***

Agent tạo **data\_model\_change** dựa trên revision tại thời điểm xử lý.

Agent không ghi đè Data Model hiện tại.

#### ***Happy Case 4 — User Accept Proposal***

Proposal được Apply nếu `base_revision == current_revision`.

#### ***Edge Case 1 — Accept Proposal cũ***

Proposal chuyển thành `CONFLICTED`.

#### ***Edge Case 2 — Hai User cùng Accept***

Database Transaction \+ Optimistic Locking đảm bảo chỉ một request cập nhật revision thành công.

#### ***Edge Case 3 — Proposal không còn phù hợp với Data Model hiện tại***

Một `Data Model Change Proposal` được tạo dựa trên một phiên bản (`base_revision`) cụ thể của Data Model. Trong thời gian Proposal đang chờ review, Data Model hiện tại có thể đã được User hoặc Proposal khác cập nhật lên revision mới.

Hệ thống **không tự động merge** Proposal cũ với Data Model mới, vì việc merge có thể làm thay đổi hoặc loại bỏ các thay đổi đã được User thực hiện trên phiên bản mới.

#### ***Edge Case 4 — Agent xử lý trong khi Data Model thay đổi***

Agent vẫn có thể hoàn thành proposal nhưng proposal không được phép ghi đè Data Model nếu base revision đã cũ.

#### ***Edge Case 5 — User mở Data Model quá lâu***

Khi lưu phải kiểm tra revision. Nếu revision đã thay đổi, yêu cầu User cập nhật trước khi tiếp tục.

#### ***Edge Case 6 — Reject Proposal***

Chỉ cập nhật trạng thái proposal thành `REJECTED`. Data Model hiện tại không thay đổi.

#### ***Edge Case 7 — Nhiều Proposal***

Trong MVP chỉ cho phép một proposal `PROPOSED` đang hoạt động trên một Data Model. Quy tắc chi tiết được kiểm soát ở Functional Requirements và Database Rules.

#### ***Edge Case 8 — Concurrent Request***

Transaction \+ Optimistic Locking phải đảm bảo không xảy ra lost update.

### **2.21 Business State & Transition Rules**

Các trạng thái quan trọng phải được quản lý theo State Machine thay vì thay đổi tùy ý.

#### ***Project***

ACTIVE

 → ANALYZING hoặc ARCHIVED

#### ***Agent Session***

ACTIVE

 → COMPLETED

 → ARCHIVED

#### ***Data Model Change***

PROPOSED

 → ACCEPTED

 → REJECTED

 → CONFLICTED

Không được chuyển trạng thái ngoài các transition đã được định nghĩa nếu không có Requirement mới được phê duyệt.

### **2.22 Error & Exception Handling**

Hệ thống phải phân biệt ít nhất các nhóm lỗi sau:

#### ***Input Error***

Input không hợp lệ hoặc thiếu dữ liệu bắt buộc.

#### ***Business Error***

Input hoặc thao tác vi phạm Business Rule.

#### ***Agent Error***

Agent không thể hoàn thành nhiệm vụ.

#### ***Tool Error***

Tool được Agent gọi thất bại.

#### ***Validation Error***

Kết quả không đáp ứng validation rules.

#### ***Conflict Error***

Dữ liệu đã thay đổi trong khi một thao tác khác đang được thực hiện.

#### ***Authorization Error***

User không có quyền thực hiện thao tác.

#### ***System Error***

Lỗi infrastructure hoặc application không thuộc các nhóm trên.

Mỗi loại lỗi phải có:

Error Condition

→ Detection

→ System Behavior

→ User-visible Result

→ Recovery Strategy

→ Logging / Audit

Chi tiết API error format được quy định tại Chương 13\.

### **2.23 Business Exceptions**

Các trường hợp đặc biệt cần được xử lý:

* Requirement quá mơ hồ.  
* Requirement thiếu thông tin.  
* Requirement mâu thuẫn.  
* Không xác định được Business Process.  
* Không xác định được KPI/Measure.  
* Không xác định được Grain.  
* Source Data thiếu schema.  
* Source Data không phù hợp với Requirement.  
* Source Data không có dữ liệu cần thiết.  
* Agent không đủ thông tin để tiếp tục.  
* Agent trả kết quả không hợp lệ.  
* Agent hoặc Tool thất bại.  
* Validation phát hiện lỗi.  
* Proposal dựa trên revision cũ.  
* Hai User cùng cập nhật Data Model.  
* User Reject kết quả.  
* User yêu cầu Agent thực hiện lại.

Khi thông tin không đủ, hệ thống phải ưu tiên yêu cầu bổ sung thông tin hoặc đánh dấu uncertainty thay vì tự tạo thông tin không có căn cứ.

### **2.24 Business Workflow End-to-End**

Workflow chính của hệ thống:

1\. Create Project

        ↓

2\. Add Project Members

        ↓

3\. Input Requirement

        ↓

4\. Input Business Rules / KPI nếu có

        ↓

5\. Input Source Data / Schema

        ↓

6\. Start AI Analysis

        ↓

7\. Requirement Analysis

        ↓

8\. Source Data Analysis

        ↓

9\. Analytical Requirement Extraction

        ↓

10\. Data Warehouse Planning

        ↓

11\. Data Model Generation

        ↓

12\. Model Validation

        ↓

13\. Critic / Review

        ↓

14\. Human Review

        ↓

15\. Accept / Edit / Reject / Retry

        ↓

16\. Approved Data Model

        ↓

17\. Generate ERD / DDL / Documentation

        ↓

18\. Complete Project

Không phải mọi workflow đều bắt buộc phải đi qua tất cả các bước trên. Functional Requirement của từng use case sẽ xác định input, output và workflow cụ thể.

### **2.25 Traceability Model**

Hệ thống phải duy trì khả năng truy xuất từ yêu cầu ban đầu đến kết quả cuối cùng.

Traceability tổng quát:

Business Requirement

        ↓

Business Rule / KPI

        ↓

Analytical Requirement

        ↓

Source Data

        ↓

Agent Analysis

        ↓

Data Warehouse Design

        ↓

Validation

        ↓

Human Review

        ↓

Approved Data Model

        ↓

ERD / DDL / Documentation

Mục tiêu là cho phép xác định:

* Data Model được tạo dựa trên Requirement nào.  
* Fact được tạo để đáp ứng Analytical Requirement nào.  
* Measure xuất phát từ KPI nào.  
* Column của Data Warehouse lấy dữ liệu từ Source nào.  
* Một Proposal thay đổi thành phần nào.  
* Agent nào tạo ra kết quả.  
* User nào phê duyệt kết quả.

### **2.26 Business/System Rules Summary**

Các nguyên tắc cốt lõi:

**BR-001 — Project Isolation**  
Dữ liệu của Project phải được phân tách theo Project boundary.

**BR-002 — Requirement Ownership**  
Mọi Requirement phải thuộc một Project.

**BR-003 — Requirement Grounding**  
Agent phải dựa trên Requirement và các input được cung cấp.

**BR-004 — No Unsupported Assumption**  
Agent không được biến thông tin chưa có căn cứ thành fact.

**BR-005 — Human Review**  
Các kết quả yêu cầu phê duyệt phải được User review trước khi trở thành kết quả chính thức.

**BR-006 — Agent Permission Boundary**  
Agent chỉ được thực hiện các hành động nằm trong quyền hạn được cấp.

**BR-007 — Data Model Protection**  
Agent không được tự ý ghi đè Data Model hiện tại khi workflow yêu cầu Proposal.

**BR-008 — Revision Validation**  
Mọi thay đổi Data Model phải kiểm tra revision.

**BR-009 — Optimistic Locking**  
Concurrent update phải được xử lý bằng transaction và optimistic locking.

**BR-010 — Conflict Safety**  
Conflict không được dẫn đến lost update hoặc overwrite dữ liệu mới hơn.

**BR-011 — Traceability**  
Kết quả quan trọng phải có khả năng truy xuất nguồn gốc khi workflow yêu cầu.

**BR-012 — Explicit Uncertainty**  
Thông tin chưa xác định phải được biểu diễn là chưa xác định hoặc cần clarification.

**BR-013 — Validation Before Approval**  
Kết quả Data Warehouse phải được validation theo các rule được quy định trước khi được phê duyệt.

**BR-014 — Requirement Priority**  
Requirement đã được Approved có mức ưu tiên cao hơn implementation hiện tại.

**BR-015 — Human Confirmation for Ambiguity**  
AI Coding Agent hoặc AI Agent không được tự ý quyết định các vấn đề chưa rõ nếu quyết định đó có thể làm thay đổi business logic, architecture, database, API hoặc security.

### **2.27 Relationship Between Business Logic and Other Requirements**

Chương 2 định nghĩa **what the system means and how it behaves**.

Các chương sau chịu trách nhiệm mô tả cách hiện thực hóa các behavior này.

| Nội dung | Chương chính |
| ----- | ----- |
| Business/System Logic | Chapter 2 |
| Use Case | Chapter 3 |
| Functional Requirements | Chapter 4 |
| Agent Architecture | Chapter 5 |
| Agent Patterns | Chapter 6 |
| Agent Specification | Chapter 7 |
| Agent Input/Output | Chapter 8 |
| LLM/Prompt | Chapter 9 |
| DW Design Rules | Chapter 10 |
| Data Source | Chapter 11 |
| Application Database | Chapter 12 |
| API | Chapter 13 |
| UI/UX | Chapter 14 |
| Security | Chapter 15 |
| Coding Standards | Chapter 16–18 |
| Testing | Chapter 19+ |
| Git/CI/CD/Deployment | Later Chapters |
| AI Coding Agent Rules | Chapter 34 |

Không được lặp lại cùng một requirement ở nhiều chương nếu không cần thiết. Nếu một rule liên quan đến nhiều tầng, một chương phải là **source of truth**, các chương khác chỉ tham chiếu đến rule đó.

### **2.28 Requirements for AI Coding Agent**

Khi implement hệ thống dựa trên tài liệu này, AI Coding Agent phải:

1. Đọc Project Overview trước khi implement.  
2. Đọc Chương 2 để hiểu business/system behavior.  
3. Đọc Use Case và Functional Requirement liên quan.  
4. Đọc architecture/design liên quan trước khi thay đổi code.  
5. Kiểm tra Database/API/UI requirements trước khi thay đổi contract tương ứng.  
6. Không tự thay đổi Business Rules.  
7. Không tự thay đổi State Transition.  
8. Không tự bỏ qua Human-in-the-Loop.  
9. Không tự thêm behavior chỉ vì implementation hiện tại thuận tiện hơn.  
10. Nếu requirement mâu thuẫn hoặc chưa đủ rõ, phải tuân thủ AI Decision-Making Rules.  
11. Khi thay đổi một behavior, phải kiểm tra ảnh hưởng đến API, Database, UI, Agent và Test.  
12. Không coi implementation hiện tại là nguồn sự thật cao hơn requirement đã được Approved.

Các quy tắc chi tiết dành riêng cho AI Coding Agent được quy định tại Chapter 34\.

### **2.29 Chapter 2 Completion Criteria**

Chương 2 được coi là đủ cơ sở để chuyển sang thiết kế Use Case khi có thể trả lời rõ các câu hỏi:

* Hệ thống quản lý những Business/System Object nào?  
* User và Project hoạt động như thế nào?  
* Requirement được tiếp nhận và xử lý ra sao?  
* Analytical Requirement được tạo như thế nào?  
* Source Data được đưa vào và phân tích như thế nào?  
* Multi-Agent được kích hoạt khi nào?  
* Agent có thể thực hiện những loại hành động nào?  
* Khi nào cần Human Review?  
* Data Model được tạo và thay đổi như thế nào?  
* Revision Conflict được xử lý ra sao?  
* Các State và State Transition là gì?  
* Các Business/System Rules quan trọng là gì?  
* Các Edge Case chính là gì?  
* Kết quả có thể trace ngược về Requirement và Source Data như thế nào?

Nếu một câu hỏi quan trọng chưa thể trả lời từ Chương 2 hoặc các chương được tham chiếu, nội dung đó phải được đánh dấu `TBD` thay vì tự suy diễn.