"""Tests for the Topic domain model."""

import pytest
from pydantic import ValidationError

from backend.models import TopicStatus
from tests.unit.factories import topic


class TestValidTopic:
    def test_valid_root_topic(self):
        t = topic(level=1)
        assert t.parent_topic_id is None
        assert t.level == 1
        assert t.status is TopicStatus.ACTIVE

    def test_valid_child_topic(self):
        t = topic(
            topic_id="TOPIC-child000001",
            name="温室气体排放",
            parent_topic_id="TOPIC-fedcba987654",
            level=2,
        )
        assert t.parent_topic_id == "TOPIC-fedcba987654"
        assert t.level == 2

    def test_child_without_explicit_level_allowed(self):
        t = topic(parent_topic_id="TOPIC-parent0000001", level=None)
        assert t.level is None

    def test_root_without_explicit_level_allowed(self):
        t = topic(level=None)
        assert t.level is None

    def test_status_accepts_lowercase_string(self):
        t = topic(status="inactive")
        assert t.status is TopicStatus.INACTIVE


class TestInvalidTopic:
    def test_root_with_level_two_rejected(self):
        with pytest.raises(ValidationError, match="level 1"):
            topic(parent_topic_id=None, level=2)

    def test_child_with_level_one_rejected(self):
        with pytest.raises(ValidationError, match="level >= 2"):
            topic(parent_topic_id="TOPIC-parent0000001", level=1)

    def test_self_parent_rejected(self):
        with pytest.raises(ValidationError, match="own parent"):
            topic(topic_id="TOPIC-fedcba987654", parent_topic_id="TOPIC-fedcba987654")

    def test_level_zero_rejected(self):
        with pytest.raises(ValidationError):
            topic(level=0)

    def test_negative_level_rejected(self):
        with pytest.raises(ValidationError):
            topic(level=-1)

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            topic(status="ACTIVE")  # wrong casing is not a value

    def test_name_required(self):
        with pytest.raises(ValidationError):
            topic(name="")

    def test_topic_id_shape(self):
        with pytest.raises(ValidationError):
            topic(topic_id="T-1")

    def test_parent_topic_id_shape(self):
        with pytest.raises(ValidationError):
            topic(parent_topic_id="ROOT-1", level=2)

    def test_assignment_validation(self):
        t = topic()
        with pytest.raises(ValidationError):
            t.status = "archived"
