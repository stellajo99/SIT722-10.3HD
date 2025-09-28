import logging
import time
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from app.db import SessionLocal, engine, get_db
from app.main import app
from app.models import Base, Order, OrderItem

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

# Suppress noisy logs from SQLAlchemy/FastAPI/Uvicorn during tests for cleaner output
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
logging.getLogger("app.main").setLevel(logging.WARNING)


# --- Pytest Fixtures ---
@pytest.fixture(scope="session", autouse=True)
def setup_database_for_tests():
    max_retries = 10
    retry_delay_seconds = 3
    for i in range(max_retries):
        try:
            logging.info(
                f"Order Service Tests: Attempting to connect to PostgreSQL for test setup (attempt {i+1}/{max_retries})..."
            )
            # Explicitly drop all tables first to ensure a clean slate for the session
            Base.metadata.drop_all(bind=engine)
            logging.info(
                "Order Service Tests: Successfully dropped all tables in PostgreSQL for test setup."
            )

            # Then create all tables required by the application
            Base.metadata.create_all(bind=engine)
            logging.info(
                "Order Service Tests: Successfully created all tables in PostgreSQL for test setup."
            )
            break
        except OperationalError as e:
            logging.warning(
                f"Order Service Tests: Test setup DB connection failed: {e}. Retrying in {retry_delay_seconds} seconds..."
            )
            time.sleep(retry_delay_seconds)
            if i == max_retries - 1:
                pytest.fail(
                    f"Could not connect to PostgreSQL for Order Service test setup after {max_retries} attempts: {e}"
                )
        except Exception as e:
            pytest.fail(
                f"Order Service Tests: An unexpected error occurred during test DB setup: {e}",
                pytrace=True,
            )

    yield


@pytest.fixture(scope="function")
def db_session_for_test():
    connection = engine.connect()
    transaction = connection.begin()
    db = SessionLocal(bind=connection)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield db
    finally:
        transaction.rollback()
        db.close()
        connection.close()
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def mock_httpx_client():
    with patch("app.main.httpx.AsyncClient") as mock_async_client_cls:
        mock_client_instance = AsyncMock()
        mock_async_client_cls.return_value.__aenter__.return_value = (
            mock_client_instance
        )
        yield mock_client_instance


# --- Order Service Tests ---
def test_read_root(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Order Service!"}


def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "order-service"}


def test_create_order_success(client: TestClient, db_session_for_test, mock_httpx_client):
    """Test successful order creation with customer validation."""
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.json.return_value = {
        "customer_id": 1,
        "email": "test@example.com",
        "shipping_address": "123 Default St"
    }
    mock_httpx_client.get.return_value.raise_for_status.return_value = None

    order_data = {
        "user_id": 1,
        "shipping_address": "456 Custom St",
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "price_at_purchase": 15.99
            },
            {
                "product_id": 2,
                "quantity": 1,
                "price_at_purchase": 29.99
            }
        ]
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["user_id"] == 1
    assert response_data["shipping_address"] == "456 Custom St"
    assert response_data["status"] == "pending"
    assert response_data["total_amount"] == 61.97  # (2 * 15.99) + (1 * 29.99)
    assert len(response_data["items"]) == 2
    assert "order_id" in response_data


def test_create_order_invalid_customer(client: TestClient, mock_httpx_client):
    """Test order creation with invalid customer ID."""
    from httpx import HTTPStatusError, Response

    # Mock customer service returning 404
    mock_response = Response(404)
    mock_httpx_client.get.side_effect = HTTPStatusError("Customer not found", request=None, response=mock_response)

    order_data = {
        "user_id": 999,
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "price_at_purchase": 15.99
            }
        ]
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "Customer 999 not found" in response.json()["detail"]


def test_create_order_empty_items(client: TestClient):
    """Test order creation with empty items list."""
    order_data = {
        "user_id": 1,
        "items": []
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 400
    assert "at least one item" in response.json()["detail"]


def test_list_orders_empty(client: TestClient):
    """Test listing orders when none exist."""
    response = client.get("/orders/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_orders_with_filters(client: TestClient, db_session_for_test, mock_httpx_client):
    """Test listing orders with filters."""
    # Mock customer service
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.json.return_value = {
        "customer_id": 1,
        "email": "test@example.com",
        "shipping_address": "123 Default St"
    }
    mock_httpx_client.get.return_value.raise_for_status.return_value = None

    # Create test orders
    order_data_1 = {
        "user_id": 1,
        "items": [{"product_id": 1, "quantity": 1, "price_at_purchase": 10.00}]
    }
    order_data_2 = {
        "user_id": 2,
        "items": [{"product_id": 2, "quantity": 1, "price_at_purchase": 20.00}]
    }

    client.post("/orders/", json=order_data_1)
    client.post("/orders/", json=order_data_2)

    # Test filter by user_id
    response = client.get("/orders/?user_id=1")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 1
    assert orders[0]["user_id"] == 1

    # Test filter by status
    response = client.get("/orders/?status=pending")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) >= 2  # Both orders should be pending


def test_get_order_success(client: TestClient, db_session_for_test, mock_httpx_client):
    """Test retrieving a specific order."""
    # Mock customer service
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.json.return_value = {
        "customer_id": 1,
        "email": "test@example.com",
        "shipping_address": "123 Default St"
    }
    mock_httpx_client.get.return_value.raise_for_status.return_value = None

    # Create order
    order_data = {
        "user_id": 1,
        "items": [{"product_id": 1, "quantity": 2, "price_at_purchase": 15.99}]
    }
    create_response = client.post("/orders/", json=order_data)
    order_id = create_response.json()["order_id"]

    # Get order
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200

    order = response.json()
    assert order["order_id"] == order_id
    assert order["user_id"] == 1
    assert len(order["items"]) == 1


def test_get_order_not_found(client: TestClient):
    """Test retrieving non-existent order."""
    response = client.get("/orders/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_update_order_status(client: TestClient, db_session_for_test, mock_httpx_client):
    """Test updating order status."""
    # Mock customer service
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.json.return_value = {
        "customer_id": 1,
        "email": "test@example.com",
        "shipping_address": "123 Default St"
    }
    mock_httpx_client.get.return_value.raise_for_status.return_value = None

    # Create order
    order_data = {
        "user_id": 1,
        "items": [{"product_id": 1, "quantity": 1, "price_at_purchase": 10.00}]
    }
    create_response = client.post("/orders/", json=order_data)
    order_id = create_response.json()["order_id"]

    # Update status
    status_data = {"status": "shipped"}
    response = client.patch(f"/orders/{order_id}/status", json=status_data)
    assert response.status_code == 200

    updated_order = response.json()
    assert updated_order["status"] == "shipped"
    assert updated_order["order_id"] == order_id


def test_update_order_status_not_found(client: TestClient):
    """Test updating status of non-existent order."""
    status_data = {"status": "shipped"}
    response = client.patch("/orders/999999/status", json=status_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_delete_order_success(client: TestClient, db_session_for_test, mock_httpx_client):
    """Test successful order deletion."""
    # Mock customer service
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.json.return_value = {
        "customer_id": 1,
        "email": "test@example.com",
        "shipping_address": "123 Default St"
    }
    mock_httpx_client.get.return_value.raise_for_status.return_value = None

    # Create order
    order_data = {
        "user_id": 1,
        "items": [{"product_id": 1, "quantity": 1, "price_at_purchase": 10.00}]
    }
    create_response = client.post("/orders/", json=order_data)
    order_id = create_response.json()["order_id"]

    # Delete order
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 204

    # Verify deletion
    get_response = client.get(f"/orders/{order_id}")
    assert get_response.status_code == 404


def test_delete_order_not_found(client: TestClient):
    """Test deleting non-existent order."""
    response = client.delete("/orders/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_get_order_items(client: TestClient, db_session_for_test, mock_httpx_client):
    """Test retrieving order items."""
    # Mock customer service
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.json.return_value = {
        "customer_id": 1,
        "email": "test@example.com",
        "shipping_address": "123 Default St"
    }
    mock_httpx_client.get.return_value.raise_for_status.return_value = None

    # Create order with multiple items
    order_data = {
        "user_id": 1,
        "items": [
            {"product_id": 1, "quantity": 2, "price_at_purchase": 15.99},
            {"product_id": 2, "quantity": 1, "price_at_purchase": 29.99}
        ]
    }
    create_response = client.post("/orders/", json=order_data)
    order_id = create_response.json()["order_id"]

    # Get order items
    response = client.get(f"/orders/{order_id}/items")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 2

    # Check first item
    assert items[0]["product_id"] == 1
    assert items[0]["quantity"] == 2
    assert items[0]["price_at_purchase"] == 15.99
    assert items[0]["item_total"] == 31.98

    # Check second item
    assert items[1]["product_id"] == 2
    assert items[1]["quantity"] == 1
    assert items[1]["price_at_purchase"] == 29.99
    assert items[1]["item_total"] == 29.99


def test_get_order_items_not_found(client: TestClient):
    """Test retrieving items for non-existent order."""
    response = client.get("/orders/999999/items")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_order_with_default_shipping_address(client: TestClient, mock_httpx_client):
    """Test order creation using customer's default shipping address."""
    # Mock customer service with default shipping address
    mock_httpx_client.get.return_value.status_code = 200
    mock_httpx_client.get.return_value.json.return_value = {
        "customer_id": 1,
        "email": "test@example.com",
        "shipping_address": "123 Default Customer St"
    }
    mock_httpx_client.get.return_value.raise_for_status.return_value = None

    order_data = {
        "user_id": 1,
        # No shipping_address provided - should use customer's default
        "items": [{"product_id": 1, "quantity": 1, "price_at_purchase": 10.00}]
    }

    response = client.post("/orders/", json=order_data)
    assert response.status_code == 201

    order = response.json()
    assert order["shipping_address"] == "123 Default Customer St"
