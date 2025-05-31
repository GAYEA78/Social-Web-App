from app.models.activity_groups import ActivityGroup, EventFrequency

RAW_ACTIVITY_GROUPS = [
    {
        "name": "Test Activity Group 1",
        "category": "Test Category 1",
        "description": "Test Description 1",
        "founding_date": "2020-01-01",
        "website": "https://example.com",
        "email": "info@example.com",
        "phone_number": "+1 (555) 555-5555",
        "social_media_links": '{"facebook":"goodbook","instagram":"goodgram"}',
        "is_active": True,
        "total_members": 0,
        "event_frequency": "weekly",
        "membership_fee": 0,
        "open_to_public": True,
        "min_age": 18,
    },
    {
        "name": "Test Activity Group 2",
        "category": "Test Category 2",
        "description": "Test Description 2",
        "founding_date": "2020-01-01",
        "website": "https://example.com",
        "email": "info@example.com",
        "phone_number": "+1 (555) 555-5555",
        "social_media_links": '{"facebook":"goodbook","instagram":"goodgram"}',
        "is_active": True,
        "total_members": 0,
        "event_frequency": "weekly",
        "membership_fee": 0,
        "open_to_public": True,
        "min_age": 18,
    },
]


def test_get_all_activity_groups(app, mock_db, mock_activity_groups_service):
    with app.app_context():
        # Arrange
        cols = list(ActivityGroup.model_fields.keys())

        rows = [tuple(d[col] for col in cols) for d in RAW_ACTIVITY_GROUPS]
        mock_db.fetchall.return_value = rows
        mock_activity_groups_service.columns = cols

        # Act
        result = mock_activity_groups_service.get_all_activity_groups()

        # Assert
        assert len(result) == 2
        assert result[0].name == "Test Activity Group 1"
        assert result[0].category == "Test Category 1"
        assert result[0].description == "Test Description 1"
        assert result[0].founding_date == "2020-01-01"
        assert result[0].website == "https://example.com"
        assert result[0].email == "info@example.com"
        assert result[0].phone_number == "+1 (555) 555-5555"
        assert result[0].social_media_links == '{"facebook":"goodbook","instagram":"goodgram"}'
        assert result[0].is_active == True
        assert result[0].total_members == 0
        assert result[0].event_frequency == EventFrequency.WEEKLY
        assert result[0].membership_fee == 0
        assert result[0].open_to_public == True
        assert result[0].min_age == 18
        assert result[1].name == "Test Activity Group 2"
        assert result[1].category == "Test Category 2"
        assert result[1].description == "Test Description 2"
        assert result[1].founding_date == "2020-01-01"
        assert result[1].website == "https://example.com"
        assert result[1].email == "info@example.com"
        assert result[1].phone_number == "+1 (555) 555-5555"
        assert result[1].social_media_links == '{"facebook":"goodbook","instagram":"goodgram"}'
        assert result[1].is_active == True
        assert result[1].total_members == 0
        assert result[1].event_frequency == EventFrequency.WEEKLY
        assert result[1].membership_fee == 0
        assert result[1].open_to_public == True
        assert result[1].min_age == 18


def test_search_activity_groups(app, mock_db, mock_activity_groups_service):
    with app.app_context():
        # Arrange
        cols = list(ActivityGroup.model_fields.keys())

        rows = [tuple(d[col] for col in cols) for d in RAW_ACTIVITY_GROUPS]
        mock_db.fetchall.return_value = rows
        mock_activity_groups_service.columns = cols

        # Act
        result = mock_activity_groups_service.search_activity_groups("1")

        # Assert
        assert len(result) == 1
        assert result[0].name == "Test Activity Group 1"
        assert result[0].category == "Test Category 1"
        assert result[0].description == "Test Description 1"
        assert result[0].founding_date == "2020-01-01"
        assert result[0].website == "https://example.com"
        assert result[0].email == "info@example.com"
        assert result[0].phone_number == "+1 (555) 555-5555"
        assert result[0].social_media_links == '{"facebook":"goodbook","instagram":"goodgram"}'
        assert result[0].is_active == True
        assert result[0].total_members == 0
        assert result[0].event_frequency == EventFrequency.WEEKLY
        assert result[0].membership_fee == 0
        assert result[0].open_to_public == True
        assert result[0].min_age == 18
