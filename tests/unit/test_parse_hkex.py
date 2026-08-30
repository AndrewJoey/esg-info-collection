"""Tests for HKEX parser structural logic (synthetic strings only)."""

from scripts.parse_hkex import (
    ASPECT_RE,
    KPI_CODE_RE,
    KPI_INLINE_RE,
    NUM_RE,
    PART_RE,
    _collect_body,
)


class TestPartMarker:
    def test_matches_part(self):
        m = PART_RE.match("A部分：引言")
        assert m and m.group(1) == "A"

    def test_matches_part_b(self):
        m = PART_RE.match("B部分：強制披露規定")
        assert m and m.group(1) == "B"

    def test_non_part_ignored(self):
        assert PART_RE.match("這是一般段落") is None


class TestAspectMarker:
    def test_matches_aspect(self):
        m = ASPECT_RE.match("層面A1： 一般披露")
        assert m and m.group(1) == "A1"

    def test_matches_aspect_b(self):
        m = ASPECT_RE.match("層面B3： 一般披露")
        assert m and m.group(1) == "B3"


class TestNumberedProvision:
    def test_matches_numbered(self):
        m = NUM_RE.match("13. 由董事會發出的聲明")
        assert m and m.group(1) == "13"

    def test_body_captured(self):
        m = NUM_RE.match("1. 合成條文內容")
        assert m.group(2) == "合成條文內容"


class TestKpiCode:
    def test_inline_code(self):
        m = KPI_INLINE_RE.search("關鍵績效指標A1.1")
        assert m and m.group(1) == "A1.1"

    def test_wrapped_code(self):
        # code on the following token
        m = KPI_CODE_RE.search("指標 A2.3")
        assert m and m.group(1) == "A2.3"

    def test_lookahead_join(self):
        # Simulate the wrapped layout: label then code on next line.
        lines = ["關鍵績效", "指標A1.1 合成指標描述"]
        joined = " ".join(lines[0:3])
        m = KPI_INLINE_RE.search(joined) or KPI_CODE_RE.search(joined)
        assert m and m.group(1) == "A1.1"


class TestCollectBody:
    def test_stops_at_next_anchor(self):
        lines = [
            "合成正文第一行",
            "合成正文第二行",
            "層面A2： 一般披露",   # next anchor
            "不應包含",
        ]
        body, nxt = _collect_body(lines, 0, "起始行")
        assert "合成正文第一行" in body
        assert "不應包含" not in body
        assert nxt == 2

    def test_stops_at_kpi(self):
        lines = ["正文", "關鍵績效", "指標A1.1 描述"]
        body, nxt = _collect_body(lines, 0, "")
        assert body == "正文"
        assert nxt == 1
