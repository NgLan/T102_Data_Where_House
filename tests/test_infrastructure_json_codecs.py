"""Kiểm thử round-trip và fail-fast của JSONB codecs."""

from uuid import uuid4

import pytest
from src.common.exceptions.infrastructure import InfrastructureException
from src.domain.data_source.constraints import (
    CheckConstraint,
    DefaultConstraint,
    ForeignKeyConstraint,
    UniqueConstraint,
)
from src.domain.data_source.enums import ColumnDataType, RelationshipType
from src.domain.data_source.value_objects import (
    ColumnMetadata,
    RelationshipMetadata,
    SchemaMetadata,
    TableMetadata,
)
from src.domain.project_session.clarification import (
    ClarificationAnswerMetadata,
    ClarificationQuestionMetadata,
)
from src.domain.project_session.enums import ClarificationAnswerKind
from src.domain.project_session.value_objects import MessageMetadata
from src.infrastructure.database.mappers.data_source.schema_metadata_codec import (
    decode_schema_metadata,
    encode_schema_metadata,
)
from src.infrastructure.database.mappers.session_event.session_event_metadata_codec import (
    decode_event_metadata,
    encode_event_metadata,
)


def test_schema_metadata_jsonb_round_trip() -> None:
    schema = SchemaMetadata(
        tables=(
            TableMetadata(
                "orders",
                (
                    ColumnMetadata(
                        "status",
                        ColumnDataType.CATEGORY,
                        null_count=1,
                        distinct_count=2,
                        distinct_values=("new", "done"),
                        constraints=(
                            ForeignKeyConstraint("statuses", "name"),
                            UniqueConstraint(),
                            CheckConstraint("status <> ''"),
                            DefaultConstraint(None),
                        ),
                    ),
                ),
            ),
        ),
        relationships=(
            RelationshipMetadata("orders.user_id", "users.id", RelationshipType.MANY_TO_ONE),
        ),
    )

    assert decode_schema_metadata(encode_schema_metadata(schema)) == schema


def test_schema_metadata_decoder_rejects_legacy_option() -> None:
    payload = {
        "tables": [
            {
                "name": "orders",
                "columns": [
                    {"name": "status", "data_type": "OPTION", "options": ["new", "done"]}
                ],
            }
        ]
    }

    with pytest.raises(InfrastructureException):
        decode_schema_metadata(payload)


def test_corrupted_schema_metadata_raises_infrastructure_error() -> None:
    with pytest.raises(InfrastructureException):
        decode_schema_metadata({"tables": "not-a-list"})


def test_session_event_metadata_round_trip() -> None:
    metadata = MessageMetadata(model="gpt-4o-mini")

    restored = decode_event_metadata(encode_event_metadata(metadata), MessageMetadata)

    assert restored == metadata


def test_corrupted_session_event_metadata_raises_infrastructure_error() -> None:
    with pytest.raises(InfrastructureException):
        decode_event_metadata({"unknown": True}, MessageMetadata)


@pytest.mark.parametrize(
    "metadata",
    [
        ClarificationQuestionMetadata(("Theo ngày", "Theo tháng"), True, "Thiếu grain"),
        ClarificationAnswerMetadata(uuid4(), ClarificationAnswerKind.OPTION, 1),
    ],
)
def test_clarification_metadata_round_trip(metadata: object) -> None:
    restored = decode_event_metadata(encode_event_metadata(metadata), type(metadata))

    assert restored == metadata
