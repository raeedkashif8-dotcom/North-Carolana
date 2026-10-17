"""TP-U-TPL-01 to 05 (TEST_PLAN.md section 1.4) and TP-CMP-09, TP-CMP-10 (template parts)."""
import pytest

from app.templates import (NotApproved, RenderError, Template, check_text_length, load_template, render,
                           sha256)

VALUES = {"buyer_first_name": "Test", "agent_name": "Demo Agent", "firm_name": "Example Realty",
          "firm_address": "100 Example St, Raleigh, NC 27601",
          "booking_link": "https://cal.com/demo-agent/buyer-consult?metadata[lead]=t1",
          "unsubscribe_link": "https://example.com/u/abc"}


def approve(*ts):
    return {(t.template_id, t.version, t.sha256) for t in ts}


@pytest.fixture
def m01():
    return load_template("templates/M-01.yaml")


@pytest.fixture
def m03():
    return load_template("templates/M-03.yaml")


def test_tpl_01_unknown_fill_in_fails_closed():
    t = Template("M-99", 1, "email", "Hi {buyer_fist_name}")
    with pytest.raises(RenderError, match="buyer_fist_name"):
        render(t, VALUES, approve(t))


def test_tpl_02_fallback_used_only_when_defined():
    with_fb = Template("M-98", 1, "email", "Hi {buyer_first_name},", fallbacks={"buyer_first_name": "there"})
    assert render(with_fb, {}, approve(with_fb)).body == "Hi there,"
    no_fb = Template("M-97", 1, "email", "Hi {buyer_first_name},")
    with pytest.raises(RenderError, match="no fallback"):
        render(no_fb, {}, approve(no_fb))


def test_tpl_03_unapproved_version_refused(m01, m03):
    v2 = Template("M-01", 2, "email", m01.body + "\nP.S. new line", m01.subject, m01.fallbacks)
    with pytest.raises(NotApproved):
        render(v2, VALUES, approve(m01, m03), explainer=m03)  # only v1 approved


def test_cmp_10_edited_text_with_same_version_refused(m01, m03):
    """Text changed in place without a new approval: the hash no longer matches."""
    tampered = Template("M-01", 1, "email", m01.body.replace("love", "hate"), m01.subject, m01.fallbacks)
    with pytest.raises(NotApproved):
        render(tampered, VALUES, approve(m01, m03), explainer=m03)


def test_tpl_04_and_cmp_09_explainer_is_byte_identical(m01, m03):
    out = render(m01, VALUES, approve(m01, m03), explainer=m03)
    assert m03.body in out.body
    start = out.body.index(m03.body)
    assert sha256(out.body[start:start + len(m03.body)]) == m03.sha256


def test_explainer_must_be_approved_too(m01, m03):
    with pytest.raises(NotApproved):
        render(m01, VALUES, approve(m01), explainer=m03)


def test_m01_renders_required_parts(m01, m03):
    out = render(m01, VALUES, approve(m01, m03), explainer=m03)
    assert VALUES["booking_link"] in out.body
    assert VALUES["firm_address"] in out.body          # CR-13
    assert VALUES["unsubscribe_link"] in out.body      # CR-13
    assert "{" not in out.body                          # nothing left unfilled


def test_tpl_05_text_over_3_segments_rejected():
    long_plain = Template("M-96", 1, "text", "a" * 460)
    with pytest.raises(RenderError, match="4 segments"):
        check_text_length(long_plain, {})
    assert check_text_length(Template("M-95", 1, "text", "a" * 459), {}) == 3
    special = Template("M-94", 1, "text", "’" * 202)  # curly apostrophe forces the 67-char segments
    with pytest.raises(RenderError):
        check_text_length(special, {})
    assert check_text_length(Template("M-93", 1, "text", "’" * 201), {}) == 3
