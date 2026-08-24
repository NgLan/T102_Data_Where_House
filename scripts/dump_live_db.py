"""Dump chính xác 100% schema và dữ liệu từ Database PostgreSQL đang chạy trên máy (Port 5434)."""

import asyncio
import json
from pathlib import Path
from uuid import UUID
import asyncpg


def format_val(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (dict, list)):
        escaped = json.dumps(v, ensure_ascii=False).replace("'", "''")
        return f"'{escaped}'::jsonb"
    if isinstance(v, UUID):
        return f"'{v}'::uuid"
    # string or datetime or other
    val_str = str(v).replace("'", "''")
    return f"'{val_str}'"


async def dump():
    url = "postgresql://postgres:ngoclan4716@127.0.0.1:5434/ai20k_db"
    conn = await asyncpg.connect(url)

    # 1. Lấy danh sách bảng theo thứ tự phụ thuộc
    ordered_tables = [
        "users",
        "projects",
        "revoked_auth_tokens",
        "project_members",
        "requirements",
        "analytical_requirements",
        "requirement_files",
        "data_sources",
        "data_models",
        "data_model_changes",
        "project_sessions",
        "session_events",
        "sandbox_configs",
    ]

    schema_lines = [
        "-- ==========================================================================",
        "-- AI20K Data Wherehouse - Database Schema (Dumped directly from LIVE local DB)",
        "-- ==========================================================================",
        "",
        "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
        "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";",
        "",
        "BEGIN;",
        "",
    ]

    data_lines = [
        "-- ==========================================================================",
        "-- AI20K Data Wherehouse - Live Data Dump (from local DB)",
        "-- ==========================================================================",
        "",
        "BEGIN;",
        "",
    ]

    # Lấy DDL từng bảng
    for tname in ordered_tables:
        # Check if table exists
        exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = $1)",
            tname
        )
        if not exists:
            continue

        schema_lines.append(f"-- ------------------------------------------------------------")
        schema_lines.append(f"-- Table: {tname}")
        schema_lines.append(f"-- ------------------------------------------------------------")
        
        # Columns
        cols = await conn.fetch("""
            SELECT column_name, data_type, udt_name, is_nullable, column_default, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = $1
            ORDER BY ordinal_position;
        """, tname)

        col_defs = []
        for c in cols:
            cname = c["column_name"]
            udt = c["udt_name"]
            is_null = c["is_nullable"] == "YES"
            default = c["column_default"]
            max_len = c["character_maximum_length"]

            type_str = udt.upper()
            if type_str == "VARCHAR" and max_len:
                type_str = f"VARCHAR({max_len})"
            elif type_str == "TIMESTAMPTZ":
                type_str = "TIMESTAMP WITH TIME ZONE"
            elif type_str == "INT4":
                type_str = "INTEGER"
            elif type_str == "INT8":
                type_str = "BIGINT"
            elif type_str == "BOOL":
                type_str = "BOOLEAN"

            col_def = f"    {cname} {type_str}"
            if default:
                col_def += f" DEFAULT {default}"
            if not is_null:
                col_def += " NOT NULL"
            col_defs.append(col_def)

        # Primary key
        pk_cols = await conn.fetch("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public' AND tc.table_name = $1
            ORDER BY kcu.ordinal_position;
        """, tname)
        if pk_cols:
            pks = ", ".join([f'"{r["column_name"]}"' for r in pk_cols])
            col_defs.append(f"    PRIMARY KEY ({pks})")

        # Foreign keys
        fks = await conn.fetch("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.delete_rule
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
            JOIN information_schema.referential_constraints AS rc
              ON rc.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public' AND tc.table_name = $1;
        """, tname)
        for fk in fks:
            del_rule = f" ON DELETE {fk['delete_rule']}" if fk['delete_rule'] else ""
            col_defs.append(
                f"    CONSTRAINT {fk['constraint_name']} FOREIGN KEY (\"{fk['column_name']}\") "
                f"REFERENCES \"{fk['foreign_table_name']}\" (\"{fk['foreign_column_name']}\"){del_rule}"
            )

        # Unique & Check constraints
        uqs = await conn.fetch("""
            SELECT tc.constraint_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'UNIQUE' AND tc.table_schema = 'public' AND tc.table_name = $1;
        """, tname)
        for uq in uqs:
            col_defs.append(f"    CONSTRAINT {uq['constraint_name']} UNIQUE (\"{uq['column_name']}\")")

        schema_lines.append(f"CREATE TABLE IF NOT EXISTS \"{tname}\" (")
        schema_lines.append(",\n".join(col_defs))
        schema_lines.append(");")
        schema_lines.append("")

        # Indexes
        indexes = await conn.fetch("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public' AND tablename = $1 AND indexname NOT LIKE '%_pkey';
        """, tname)
        for idx in indexes:
            idef = idx["indexdef"]
            idef = idef.replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ", 1)
            idef = idef.replace("CREATE UNIQUE INDEX ", "CREATE UNIQUE INDEX IF NOT EXISTS ", 1)
            schema_lines.append(f"{idef};")
        schema_lines.append("")

        # ----------------- DUMP DATA -----------------
        rows = await conn.fetch(f'SELECT * FROM "{tname}"')
        if rows:
            data_lines.append(f"-- Data for: {tname} ({len(rows)} rows)")
            col_names = list(rows[0].keys())
            cols_str = ", ".join([f'"{c}"' for c in col_names])

            batch_size = 50
            for i in range(0, len(rows), batch_size):
                batch = rows[i : i + batch_size]
                val_rows = []
                for row in batch:
                    vals = [format_val(row[col]) for col in col_names]
                    val_rows.append(f"  ({', '.join(vals)})")
                
                insert_stmt = f"INSERT INTO \"{tname}\" ({cols_str}) VALUES\n" + ",\n".join(val_rows) + "\nON CONFLICT DO NOTHING;"
                data_lines.append(insert_stmt)
                data_lines.append("")

    schema_lines.append("COMMIT;")
    data_lines.append("COMMIT;")

    root_dir = Path(__file__).resolve().parent.parent

    # 1. init_supabase_schema.sql (Schema Only)
    schema_file = root_dir / "init_supabase_schema.sql"
    schema_file.write_text("\n".join(schema_lines), encoding="utf-8")
    print(f"[OK] Wrote schema to: {schema_file}")

    # 2. init_supabase_full_dump.sql (Schema + All Live Data)
    full_content = "\n".join(schema_lines[:-1]) + "\n\n" + "\n".join(data_lines[4:])
    full_file = root_dir / "init_supabase_full_dump.sql"
    full_file.write_text(full_content, encoding="utf-8")
    print(f"[OK] Wrote full schema + live data to: {full_file}")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(dump())
