import { Icon } from "./icon";

interface TableNodeProps {
  className: string;
  title: string;
  role: "FACT" | "DIM";
  columns: Array<{ name: string; type: string; key?: "PK" | "FK" }>;
}

/** Hiển thị một bảng trong sơ đồ ERD minh họa. */
function TableNode({ className, title, role, columns }: TableNodeProps) {
  return (
    <article className={`absolute z-10 w-48 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-[0_12px_32px_rgba(15,23,42,0.09)] ${className}`}>
      <header className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-3 py-2.5">
        <span className="text-[11px] font-bold text-slate-800">{title}</span>
        <span className={`rounded px-1.5 py-0.5 text-[8px] font-extrabold tracking-wider ${role === "FACT" ? "bg-blue-100 text-blue-700" : "bg-violet-100 text-violet-700"}`}>
          {role}
        </span>
      </header>
      <div className="py-1.5">
        {columns.map((column) => (
          <div key={column.name} className="flex items-center gap-2 px-3 py-1 text-[9px]">
            <span className={`w-5 font-bold ${column.key === "PK" ? "text-amber-500" : column.key === "FK" ? "text-blue-500" : "text-slate-300"}`}>
              {column.key ?? "·"}
            </span>
            <span className="flex-1 font-medium text-slate-600">{column.name}</span>
            <span className="text-slate-400">{column.type}</span>
          </div>
        ))}
      </div>
    </article>
  );
}

/** Hiển thị canvas mô hình dữ liệu làm ngữ cảnh cho phần phân tích AI. */
export function DataModelCanvas() {
  return (
    <section className="flex min-h-[480px] flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
          <Icon name="network" className="size-[18px] text-blue-600" />
          Sơ đồ quan hệ
          <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700">Đã đồng bộ</span>
        </div>
        <div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 text-slate-500">
          <button type="button" aria-label="Thu nhỏ sơ đồ" className="grid size-7 place-items-center rounded hover:bg-white">−</button>
          <span className="px-1 text-[10px] font-semibold">82%</span>
          <button type="button" aria-label="Phóng to sơ đồ" className="grid size-7 place-items-center rounded hover:bg-white">+</button>
        </div>
      </header>
      <div className="erd-grid relative min-h-[430px] flex-1 overflow-hidden bg-[#f8fafc]">
        <svg className="absolute inset-0 size-full text-blue-300" aria-hidden="true">
          <path d="M 280 214 C 350 214, 350 93, 430 93" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="5 5" />
          <path d="M 280 214 C 350 214, 350 214, 430 214" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="5 5" />
          <path d="M 280 214 C 350 214, 350 335, 430 335" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="5 5" />
        </svg>
        <TableNode
          className="left-[8%] top-[133px]"
          title="Fact_Rides"
          role="FACT"
          columns={[
            { name: "ride_key", type: "BIGINT", key: "PK" },
            { name: "driver_key", type: "INT", key: "FK" },
            { name: "customer_key", type: "INT", key: "FK" },
            { name: "fare_amount", type: "DECIMAL" },
            { name: "created_at", type: "TIMESTAMP" },
          ]}
        />
        <TableNode
          className="left-[57%] top-5"
          title="Dim_Driver"
          role="DIM"
          columns={[
            { name: "driver_key", type: "INT", key: "PK" },
            { name: "driver_id", type: "VARCHAR" },
            { name: "vehicle_type", type: "VARCHAR" },
          ]}
        />
        <TableNode
          className="left-[57%] top-[142px]"
          title="Dim_Customer"
          role="DIM"
          columns={[
            { name: "customer_key", type: "INT", key: "PK" },
            { name: "phone_number", type: "VARCHAR" },
            { name: "member_tier", type: "VARCHAR" },
          ]}
        />
        <TableNode
          className="left-[57%] top-[264px]"
          title="Dim_Promo"
          role="DIM"
          columns={[
            { name: "promo_key", type: "INT", key: "PK" },
            { name: "promo_code", type: "VARCHAR" },
            { name: "discount_type", type: "VARCHAR" },
          ]}
        />
        <div className="absolute bottom-4 left-4 flex items-center gap-2 rounded-lg border border-slate-200 bg-white/90 px-3 py-2 text-[10px] text-slate-500 shadow-sm backdrop-blur">
          <span className="size-2 rounded-full bg-blue-500" /> 1 bảng Fact
          <span className="ml-2 size-2 rounded-full bg-violet-500" /> 3 bảng Dimension
        </div>
      </div>
    </section>
  );
}
