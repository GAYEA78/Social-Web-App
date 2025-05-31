from unittest.mock import MagicMock


def test_notify_waitlist_success(monkeypatch, client, login_user):
    mock_event = MagicMock()
    mock_event.notify_waitlist.return_value = {"success": True, "message": "User notified"}
    monkeypatch.setattr("app.models.events.Event", mock_event)

    response = client.post("/events/1/notify_waitlist")
    assert response.status_code == 302  # Redirect after success
    mock_event.notify_waitlist.assert_called_once_with(1)


def test_notify_waitlist_failure(monkeypatch, client, login_user):
    mock_event = MagicMock()
    mock_event.notify_waitlist.return_value = {
        "success": False,
        "message": "No users on the waitlist",
    }
    monkeypatch.setattr("app.models.events.Event", mock_event)

    response = client.post("/events/1/notify_waitlist")
    assert response.status_code == 302  # Redirect after failure
    mock_event.notify_waitlist.assert_called_once_with(1)


def test_confirm_waitlist_success(monkeypatch, client, login_user):
    mock_event = MagicMock()
    mock_event.confirm_waitlist.return_value = {
        "success": True,
        "message": "Waitlist spot confirmed and registered",
    }
    monkeypatch.setattr("app.models.events.Event", mock_event)

    response = client.post("/events/1/confirm_waitlist", data={"user_id": 2})
    assert response.status_code == 302  # Redirect after success
    mock_event.confirm_waitlist.assert_called_once_with(1, 2)


def test_confirm_waitlist_failure(monkeypatch, client, login_user):
    mock_event = MagicMock()
    mock_event.confirm_waitlist.return_value = {
        "success": False,
        "message": "No notification found for this user",
    }
    monkeypatch.setattr("app.models.events.Event", mock_event)

    response = client.post("/events/1/confirm_waitlist", data={"user_id": 2})
    assert response.status_code == 302  # Redirect after failure
    mock_event.confirm_waitlist.assert_called_once_with(1, 2)
