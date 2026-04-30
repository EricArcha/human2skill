import pytest

from human2skill.schemas import SchemaValidationError, load_schema, validate_document


def test_load_schema_reads_existing_schema():
    schema = load_schema("person.meta.schema.json")

    assert schema["type"] == "object"
    assert "properties" in schema


def test_validate_document_raises_readable_error():
    with pytest.raises(SchemaValidationError) as error:
        validate_document("person.meta.schema.json", {"schema_version": "1"})

    assert "person.meta.schema.json" in str(error.value)
    assert "required" in str(error.value)
