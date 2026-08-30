"""Tests for the Framework domain model."""

import pytest
from pydantic import ValidationError

from backend.models import FrameworkType, generate_framework_id
from tests.unit.factories import framework


class TestValidFramework:
    @pytest.mark.parametrize(
        ("code", "framework_type"),
        [
            ("SSE", FrameworkType.EXCHANGE_RULE),
            ("HKEX", FrameworkType.EXCHANGE_RULE),
            ("GRI", FrameworkType.REPORTING_STANDARD),
            ("MSCI", FrameworkType.RATING_METHODOLOGY),
            ("CSA-COS", FrameworkType.RATING_QUESTIONNAIRE),
        ],
    )
    def test_all_five_v0_sources_are_representable(self, code, framework_type):
        fw = framework(
            framework_id=generate_framework_id(code),
            code=code,
            name=f"{code} source",
            framework_type=framework_type,
        )
        assert fw.framework_id == f"FW-{code}"
        assert fw.framework_type is framework_type

    def test_defaults_timestamps(self):
        fw = framework()
        assert fw.created_at is not None
        assert fw.updated_at is not None

    def test_category_accepts_lowercase_string(self):
        fw = framework(framework_type="reporting_standard")
        assert fw.framework_type is FrameworkType.REPORTING_STANDARD


class TestInvalidFramework:
    def test_invalid_category_rejected(self):
        with pytest.raises(ValidationError):
            framework(framework_type="clause_library")

    def test_category_casing_is_significant(self):
        # DATA_MODEL uses lowercase snake_case values; uppercase is not
        # an alternative name.
        with pytest.raises(ValidationError):
            framework(framework_type="EXCHANGE_RULE")

    def test_framework_id_must_use_fw_prefix(self):
        with pytest.raises(ValidationError):
            framework(framework_id="FRAMEWORK-HKEX")

    @pytest.mark.parametrize("field", ["code", "name", "publisher", "status"])
    def test_required_fields_cannot_be_empty(self, field):
        with pytest.raises(ValidationError):
            framework(**{field: ""})

    def test_missing_framework_type_rejected(self):
        with pytest.raises(ValidationError):
            framework(framework_type=None)
