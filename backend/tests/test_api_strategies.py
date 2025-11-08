"""
API tests for strategies endpoints
"""
import pytest
from fastapi import status

STRATEGIES_ENDPOINT = "/api/v1/strategies/"


@pytest.mark.api
@pytest.mark.integration
class TestStrategiesAPI:
    """Test strategies API endpoints"""

    @pytest.mark.asyncio
    async def test_create_strategy(self, async_client, sample_strategy_data):
        """Test creating a strategy"""
        response = await async_client.post(STRATEGIES_ENDPOINT, json=sample_strategy_data)
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["name"] == sample_strategy_data["name"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_strategies(self, async_client, sample_strategy_data):
        """Test getting all strategies"""
        await async_client.post(STRATEGIES_ENDPOINT, json=sample_strategy_data)

        response = await async_client.get(STRATEGIES_ENDPOINT)
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_get_strategy_by_id(self, async_client, sample_strategy_data):
        """Test getting a strategy by ID"""
        create_response = await async_client.post(STRATEGIES_ENDPOINT, json=sample_strategy_data)
        strategy_id = create_response.json()["id"]

        response = await async_client.get(f"{STRATEGIES_ENDPOINT}{strategy_id}")
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["id"] == strategy_id
        assert data["name"] == sample_strategy_data["name"]

    @pytest.mark.asyncio
    async def test_update_strategy(self, async_client, sample_strategy_data):
        """Test updating a strategy"""
        create_response = await async_client.post(STRATEGIES_ENDPOINT, json=sample_strategy_data)
        strategy_id = create_response.json()["id"]

        update_data = {"name": "Updated Strategy Name"}
        response = await async_client.put(f"{STRATEGIES_ENDPOINT}{strategy_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data["name"] == "Updated Strategy Name"

    @pytest.mark.asyncio
    async def test_delete_strategy(self, async_client, sample_strategy_data):
        """Test deleting a strategy"""
        create_response = await async_client.post(STRATEGIES_ENDPOINT, json=sample_strategy_data)
        strategy_id = create_response.json()["id"]

        response = await async_client.delete(f"{STRATEGIES_ENDPOINT}{strategy_id}")
        assert response.status_code == status.HTTP_200_OK, response.text

        get_response = await async_client.get(f"{STRATEGIES_ENDPOINT}{strategy_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_activate_strategy(self, async_client, sample_strategy_data):
        """Test activating a strategy"""
        create_response = await async_client.post(STRATEGIES_ENDPOINT, json=sample_strategy_data)
        strategy_id = create_response.json()["id"]

        response = await async_client.post(f"{STRATEGIES_ENDPOINT}{strategy_id}/activate")
        assert response.status_code == status.HTTP_200_OK, response.text

        get_response = await async_client.get(f"{STRATEGIES_ENDPOINT}{strategy_id}")
        assert get_response.json()["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_strategy_validation(self, async_client):
        """Test strategy creation validation"""
        invalid_data = {"name": "Test"}
        response = await async_client.post(STRATEGIES_ENDPOINT, json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
