def test_status_endpoint(client):
    response = client.get("/status/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["service"] == "project-1-online-commerce"
    assert data["status"] == "healthy"
    assert "timestamp" in data
