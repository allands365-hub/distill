from pod.functions.split_batch.code import split_items as split_batch


def test_splits_on_triple_dash():
    raw = "first report\n---\nsecond report"
    items = split_batch(raw)
    assert len(items) == 2
    assert items[0]["body"] == "first report"
    assert items[1]["body"] == "second report"


def test_parses_channel_and_title_headers():
    raw = "Channel: slack\nTitle: App crashes\nIt crashes on launch every time."
    items = split_batch(raw)
    assert items[0]["channel"] == "slack"
    assert items[0]["title"] == "App crashes"
    assert items[0]["body"] == "It crashes on launch every time."


def test_missing_headers_default_to_other_and_empty_title():
    items = split_batch("just some text")
    assert items[0]["channel"] == "other"
    assert items[0]["title"] == ""
    assert items[0]["body"] == "just some text"


def test_drops_blank_items():
    raw = "real item\n---\n   \n---\nanother"
    items = split_batch(raw)
    assert len(items) == 2


def test_empty_input_returns_empty_list():
    assert split_batch("") == []
    assert split_batch("   \n  ") == []


def test_headers_recognized_after_leading_blank_lines():
    # A blank line before the headers must not break header parsing.
    raw = "\n\nChannel: github\nTitle: Broken export\nExport yields an empty file."
    items = split_batch(raw)
    assert items[0]["channel"] == "github"
    assert items[0]["title"] == "Broken export"
    assert items[0]["body"] == "Export yields an empty file."


def test_text_after_body_is_not_parsed_as_header():
    # A 'Title:'-looking line that appears after real body text stays in the body.
    raw = "Something broke.\nTitle: not a header here"
    items = split_batch(raw)
    assert items[0]["title"] == ""
    assert "Title: not a header here" in items[0]["body"]
