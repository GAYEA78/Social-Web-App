from unittest.mock import MagicMock

from app.models.activity_groups import ActivityGroup, EventFrequency

DUMMY_FREE_ACTIVITY_GROUP = ActivityGroup(
    name="Test Group",
    category="fun",
    description="desc",
    founding_date="2021-01-01",
    website="http://example.com",
    email="x@y.com",
    phone_number="123",
    total_members=5,
    social_media_links="{}",
    event_frequency=EventFrequency.WEEKLY,
    membership_fee=0,
    open_to_public=False,
    is_active=True,
    min_age=18,
)

DUMMY_PAID_ACTIVITY_GROUP = ActivityGroup(
    name="Test Group",
    category="fun",
    description="desc",
    founding_date="2021-01-01",
    website="http://example.com",
    email="x@y.com",
    phone_number="123",
    total_members=5,
    social_media_links="{}",
    event_frequency=EventFrequency.WEEKLY,
    membership_fee=50,
    open_to_public=True,
    is_active=True,
    min_age=18,
)


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"You can't spell Boston without activities" in response.data


def test_index_no_category_calls_get_all_and_shows_no_results(monkeypatch, client):
    mock_svc = MagicMock()
    mock_svc.get_all_activity_groups.return_value = []
    monkeypatch.setattr("app.routes.main.ActivityGroupsService", lambda: mock_svc)

    resp = client.get("/")
    assert resp.status_code == 200

    mock_svc.get_all_activity_groups.assert_called_once()
    mock_svc.search_activity_groups.assert_not_called()

    assert b"No activities found" in resp.data


def test_index_displays_group_and_free_label(monkeypatch, client):
    mock_svc = MagicMock()
    mock_svc.get_all_activity_groups.return_value = [DUMMY_FREE_ACTIVITY_GROUP]
    monkeypatch.setattr("app.routes.main.ActivityGroupsService", lambda: mock_svc)

    resp = client.get("/")
    html = resp.data.decode()

    assert "Free" in html
    assert "<strong>Age:</strong> 18+" in html


def test_index_with_category_calls_search_and_displays_fee_and_public(monkeypatch, client):
    mock_svc = MagicMock()
    mock_svc.search_activity_groups.return_value = [DUMMY_PAID_ACTIVITY_GROUP]
    monkeypatch.setattr("app.routes.main.ActivityGroupsService", lambda: mock_svc)

    resp = client.get("/?category=choir")
    assert resp.status_code == 200

    mock_svc.search_activity_groups.assert_called_once_with("choir")
    mock_svc.get_all_activity_groups.assert_not_called()

    html = resp.data.decode()
    assert "$50" in html
    assert "<strong>Open to public:</strong> Yes" in html
