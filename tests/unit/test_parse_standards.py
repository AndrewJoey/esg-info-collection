"""Tests for GRI/MSCI/CSA-COS parser logic (synthetic strings only)."""

import re

from scripts.parse_gri import (
    DISCLOSURE_RE,
    SECTION_MARKERS,
    STD_HEADER_RE,
    SUPERSEDE_RE,
    SECTOR_NUMBERS,
)
from scripts.parse_msci import SCORE_HEADING_RE, _is_heading, KNOWN_HEADINGS
from scripts.parse_csa_cos import FIELD_LABELS, NON_HEADING_PREFIXES


class TestGRIRegex:
    def test_standard_header(self):
        m = STD_HEADER_RE.search("GRI 305: Emissions 2016")
        assert m.group(1) == "305" and m.group(3) == "2016"

    def test_disclosure_line(self):
        m = DISCLOSURE_RE.match("Disclosure 305-1 Direct (Scope 1) GHG emissions")
        assert m.group(1) == "305-1"

    def test_supersession_from_text(self):
        m = SUPERSEDE_RE.search(
            "Disclosures 305-1 to 305-5 have been superseded by GRI 102: Climate Change 2025"
        )
        assert m and "GRI 102" in m.group(1)

    def test_section_markers(self):
        assert "REQUIREMENTS" in SECTION_MARKERS
        assert "GUIDANCE" in SECTION_MARKERS
        assert "RECOMMENDATIONS" in SECTION_MARKERS

    def test_sector_numbers(self):
        # GRI 11-14 are sector standards, not auto-applied.
        assert "11" in SECTOR_NUMBERS
        assert "305" not in SECTOR_NUMBERS


class TestMSCIHeadings:
    def test_known_heading(self):
        assert _is_heading("Introduction")
        assert _is_heading("Risks associated with this Key Issue")

    def test_score_heading_pattern(self):
        assert _is_heading("Carbon Emissions Key Issue score")
        assert _is_heading("Carbon Emissions Management score")

    def test_body_text_not_heading(self):
        assert not _is_heading("Increased costs linked to carbon pricing.")


class TestCSALabels:
    def test_field_labels(self):
        assert "Question Rationale" in FIELD_LABELS
        assert "Assessment Focus" in FIELD_LABELS

    def test_non_heading_prefixes(self):
        # "No changes from 2025" is a field value, not a criterion name.
        assert "No changes from 2025".startswith(NON_HEADING_PREFIXES)
        # A real criterion name is not filtered.
        assert not "Board Gender Diversity".startswith(NON_HEADING_PREFIXES)
