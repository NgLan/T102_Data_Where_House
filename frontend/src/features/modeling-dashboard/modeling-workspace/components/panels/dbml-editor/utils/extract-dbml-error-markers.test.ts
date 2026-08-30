import { describe, expect, it } from "vitest";
import { parseDbml } from "../../../../model-document/dbml/dbml-adapter";
import { extractDbmlErrorMarkers } from "./extract-dbml-error-markers";

describe("extractDbmlErrorMarkers", () => {
  it("trả về mảng rỗng nếu không có lỗi cú pháp hay validation", () => {
    const markers = extractDbmlErrorMarkers({
      code: "Table users {\n  id int [pk]\n}",
      syntaxErrors: [],
      parseError: null,
      validationIssues: [],
    });
    expect(markers).toEqual([]);
  });

  it("xử lý nhiều dòng lỗi bất kỳ như input của người dùng", () => {
    const code = "csdklnd\ndvsmkvlđ\nvsdvdvd\ndsvdsvlds";
    const parsed = parseDbml(code);
    console.log("PARSED ON USER INPUT:", JSON.stringify(parsed));
    const markers = extractDbmlErrorMarkers({
      code,
      syntaxErrors: parsed.syntaxErrors,
      parseError: parsed.error,
    });
    console.log("MARKERS ON USER INPUT:", JSON.stringify(markers));
    expect(markers.length).toBeGreaterThan(0);
  });

  it("trích xuất đúng marker từ syntaxErrors với vị trí dòng và cột", () => {
    const code = "Table users {\n  id in\n}";
    const markers = extractDbmlErrorMarkers({
      code,
      syntaxErrors: [
        {
          line: 2,
          column: 3,
          endLine: 2,
          endColumn: 8,
          message: "Expect a type",
        },
      ],
      parseError: "DATA_MODEL_DBML_SYNTAX_INVALID",
    });

    expect(markers).toHaveLength(1);
    expect(markers[0]).toEqual({
      line: 2,
      column: 3,
      endColumn: 8,
      message: "Expect a type",
      severity: "error",
    });
  });

  it("tạo marker cho semantic validation issues của bảng và cột", () => {
    const code = `Table Fact_DieuTri {
  id int [pk]
  benh_nhan_key int
}`;
    const markers = extractDbmlErrorMarkers({
      code,
      validationIssues: [
        {
          code: "TABLE_PRIMARY_KEY_MISSING",
          table_name: "Fact_DieuTri",
          column_name: "benh_nhan_key",
          severity: "ERROR",
          title: "Thiếu khóa chính",
          description: "Cột benh_nhan_key không hợp lệ",
        },
      ],
    });

    expect(markers).toHaveLength(1);
    expect(markers[0].line).toBe(3);
    expect(markers[0].message).toContain("Thiếu khóa chính");
  });
});
