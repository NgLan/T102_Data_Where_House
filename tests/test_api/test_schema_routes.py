import pytest


@pytest.mark.asyncio
async def test_generate_schema_8step_pipeline_endpoint(client):
    """Test API POST /api/v1/agent/generate-schema qua 8 bước luồng dữ liệu pipeline."""
    payload = {
        "project_id": "analytics-prod-2026",
        "dataset_id": "ecommerce_dw",
        "business_requirements": "Cần thiết kế Data Mart bán hàng gồm Đơn hàng, Khách hàng, SĐT 0901234567 và Sản phẩm để phân tích doanh thu.",
        "uploaded_tables": [
            {
                "table_name": "raw_orders_oltp",
                "raw_schema_ddl": "CREATE TABLE raw_orders_oltp (id INT, customer_id INT, amount NUMERIC);",
            }
        ],
        "sql_dialect": "bigquery",
        "enable_pii_masking": True,
        "enable_rag_context": True,
        "hitl_refinement_comments": "Vui lòng nhóm bảng theo cụm danh mục sản phẩm.",
    }
    response = await client.post("/api/v1/agent/generate-schema", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "success"
    assert body["code"] == 200

    data = body["data"]
    assert "schema_id" in data
    assert data["pii_masked"] is True
    assert data["rag_context_applied"] is True

    # Bước 5: Verify Mermaid ERD for Interactive Canvas
    assert "mermaid_erd" in data
    assert "erDiagram" in data["mermaid_erd"]

    # Bước 7 & 8: Verify Sandbox DB Execution Plan
    assert "sandbox_execution_plan" in data
    assert data["sandbox_execution_plan"]["sandbox_schema_prefix"] == "sandbox_schema"
    assert len(data["sandbox_execution_plan"]["execution_logs"]) > 0

    # Verify 5 mandatory schema elements
    tables = data["tables"]
    assert len(tables) > 0
    for table in tables:
        assert table["table_type"] in ["Fact", "Dimension", "Bridge", "Aggregate"]
        assert "grain" in table and len(table["grain"]) > 0
        assert "primary_key" in table
        assert "foreign_keys" in table
        assert "ddl_sql" in table and "CREATE OR REPLACE TABLE" in table["ddl_sql"]

    # Verify Critic Agent Anti-pattern warnings
    assert "anti_pattern_warnings" in data
    assert isinstance(data["anti_pattern_warnings"], list)


@pytest.mark.asyncio
async def test_validate_schema_critic_agent_endpoint(client):
    """Test API POST /api/v1/agent/validate-schema với Critic Agent Audit."""
    payload = {
        "ddl_sql_content": "CREATE TABLE `proj.ds.fact_sales` (sale_id STRING, amount NUMERIC);",
        "sql_dialect": "bigquery",
    }
    response = await client.post("/api/v1/agent/validate-schema", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "success"
    data = body["data"]
    assert "is_valid" in data
    assert "score" in data
    assert "anti_pattern_warnings" in data

    warnings = data["anti_pattern_warnings"]
    assert any(w["code"] == "CRIT_MISSING_PK" for w in warnings)
    assert any(w["code"] == "WARN_BQ_MISSING_PARTITION" for w in warnings)
