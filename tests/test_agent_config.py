"""TP-U-CFG-01 to 03, TP-U-RM-11, TP-U-TZ-06 (TEST_PLAN.md sections 1.2, 1.3, 1.9)."""
import copy

import pytest
import yaml

from app.agent_config import ConfigError, load_agent_config

BASE = yaml.safe_load(open("agents/demo-agent.yaml", encoding="utf-8"))


def write(tmp_path, data):
    p = tmp_path / "agent.yaml"
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    return p


def variant(**changes):
    d = copy.deepcopy(BASE)
    for dotted, value in changes.items():
        node = d
        *path, last = dotted.split("__")
        for k in path:
            node = node[k]
        if value is DELETE:
            del node[last]
        else:
            node[last] = value
    return d


DELETE = object()


def test_demo_agent_config_is_valid():
    cfg = load_agent_config("agents/demo-agent.yaml")
    assert cfg.agent_id == "demo-agent" and cfg.status == "test"
    assert cfg.sms.enabled is False


def test_cfg_01_missing_firm_address(tmp_path):
    with pytest.raises(ConfigError) as e:
        load_agent_config(write(tmp_path, variant(firm_address=DELETE)))
    assert any("firm_address" in p for p in e.value.problems)


@pytest.mark.parametrize("offsets", [[12, 72, 168], [24, 30, 168]])
def test_rm_11_and_cfg_02_reminder_offsets(tmp_path, offsets):
    with pytest.raises(ConfigError, match="20 hours"):
        load_agent_config(write(tmp_path, variant(reminders__offsets_hours=offsets)))


def test_tz_06_and_cfg_03_window_outside_hard_limit(tmp_path):
    with pytest.raises(ConfigError, match="08:00 to 21:00"):
        load_agent_config(write(tmp_path, variant(reminders__window={"start": "07:00", "end": "22:00"})))


def test_max_reminders_hard_cap(tmp_path):
    with pytest.raises(ConfigError, match="hard cap"):
        load_agent_config(write(tmp_path, variant(reminders__max=6,
                                                  reminders__offsets_hours=[24, 48, 72, 96, 120, 144])))


def test_typo_in_key_is_an_error(tmp_path):
    with pytest.raises(ConfigError, match="reminderz"):
        load_agent_config(write(tmp_path, variant(reminderz={"x": 1})))


def test_draft_mode_needs_docusign(tmp_path):
    with pytest.raises(ConfigError, match="DocuSign"):
        load_agent_config(write(tmp_path, variant(agreement__esign="dotloop")))


def test_unknown_time_zone(tmp_path):
    with pytest.raises(ConfigError, match="time zone"):
        load_agent_config(write(tmp_path, variant(timezone="America/Raleigh")))
