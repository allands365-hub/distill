from pod.functions.detect_duplicates import detect_duplicates


EXISTING = [
    {"id": "issue_1", "title": "Login button does nothing",
     "body": "Clicking login has no effect on the page."},
    {"id": "issue_2", "title": "Dark mode request",
     "body": "Please add a dark theme."},
]


def test_finds_near_duplicate_and_links():
    item = {"title": "Login button not working",
            "body": "The login button doesn't respond when clicked."}
    r = detect_duplicates(item, EXISTING, threshold=0.4)
    assert r["linked_to"] == "issue_1"
    assert r["candidates"][0]["id"] == "issue_1"
    assert r["candidates"][0]["score"] >= r["candidates"][-1]["score"]


def test_no_link_when_below_threshold():
    item = {"title": "Export to CSV", "body": "Add a CSV export option to reports."}
    r = detect_duplicates(item, EXISTING, threshold=0.6)
    assert r["linked_to"] is None


def test_empty_existing_returns_no_link():
    r = detect_duplicates({"title": "x", "body": "y"}, [], threshold=0.6)
    assert r["linked_to"] is None
    assert r["candidates"] == []
