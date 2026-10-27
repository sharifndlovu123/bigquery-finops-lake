from ladder import decide


def test_escalates_with_spend():
    assert [decide(p, "dev") for p in (10, 50, 90)] == ["none", "notify_team", "open_ticket"]


def test_dev_is_stopped_at_100():
    assert decide(100, "dev") == "stop_resources"


def test_prod_is_never_stopped_automatically():
    assert decide(120, "prod") == "page_owner"
