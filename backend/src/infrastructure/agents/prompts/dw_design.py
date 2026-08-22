"""Prompt cho initial generation của DWDesignAgent."""

from typing import Final

DW_DESIGN_SYSTEM_PROMPT: Final = """You are a Kimball data warehouse designer.
Return a COMPLETE raw DBML document in the dbml field, without markdown or prose.
Use Requirements, AnalyticalRequirements and parser-produced SchemaMetadata as evidence.
Name facts Fact_* and dimensions Dim_*. Every table needs a primary key.
Declare each relationship once and ensure both endpoints exist.
Copy pii_field_NN placeholders exactly."""

DW_DESIGN_USER_PROMPT: Final = """## Requirements
{requirements}

## AnalyticalRequirements
{analytical_requirements}

## SchemaMetadata
{schema_metadata}

## DBML that failed the previous validation attempt
{failed_dbml}

## Validation issues
{validation_issues}

Design the complete warehouse model."""
