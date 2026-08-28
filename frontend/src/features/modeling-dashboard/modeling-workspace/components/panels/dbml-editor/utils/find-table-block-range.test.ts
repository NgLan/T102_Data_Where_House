import { describe, expect, it } from "vitest";
import { findTableBlockRange } from "./find-table-block-range";

describe("findTableBlockRange", () => {
  it("trả về null nếu tên bảng hoặc mã nguồn rỗng", () => {
    expect(findTableBlockRange("", "users")).toBeNull();
    expect(findTableBlockRange("Table users {}", "")).toBeNull();
  });

  it("tìm chính xác phạm vi của bảng Fact_DieuTri", () => {
    const code = `Table Dim_BenhNhan {
  id int [pk]
}

Table Fact_DieuTri {
    dieu_tri_key int [pk, increment]
    benh_nhan_key int [not null]
    thoi_gian_key int [not null]
    khoa_key int [not null]
    chuan_doan_key int [not null]
    so_ngay_dieu_tri int [not null]
}

Table Dim_Khoa {
  id int [pk]
}`;
    const range = findTableBlockRange(code, "Fact_DieuTri");
    expect(range).not.toBeNull();
    const extracted = code.slice(range!.startPos, range!.endPos);
    expect(extracted).toContain("Table Fact_DieuTri {");
    expect(extracted).toContain("so_ngay_dieu_tri int [not null]");
    expect(extracted.endsWith("}")).toBe(true);
    expect(extracted).not.toContain("Dim_Khoa");
    expect(extracted).not.toContain("Dim_BenhNhan");
  });

  it("xử lý đúng bảng có khối lồng nhau (indexes, note) và chuỗi", () => {
    const code = `Table Orders {
  id int [pk]
  note varchar [note: 'note with {brace}']
  indexes {
    id [name: 'idx_order_id']
  }
}`;
    const range = findTableBlockRange(code, "Orders");
    expect(range).not.toBeNull();
    expect(code.slice(range!.startPos, range!.endPos)).toBe(code);
  });
});
