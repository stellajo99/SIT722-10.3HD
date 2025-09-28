import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas import (
    OrderItemCreate, OrderItemResponse, OrderCreate, OrderUpdate,
    OrderResponse, OrderStatusUpdate
)


class TestOrderItemSchemas:
    """Unit tests for OrderItem Pydantic schemas."""

    def test_order_item_create_valid(self):
        """Test creating a valid OrderItemCreate schema."""
        data = {
            "product_id": 1,
            "quantity": 2,
            "price_at_purchase": 15.99
        }

        order_item = OrderItemCreate(**data)
        assert order_item.product_id == 1
        assert order_item.quantity == 2
        assert order_item.price_at_purchase == 15.99

    def test_order_item_create_invalid_product_id(self):
        """Test OrderItemCreate with invalid product_id."""
        data = {
            "product_id": 0,  # Should be >= 1
            "quantity": 2,
            "price_at_purchase": 15.99
        }

        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(**data)

        assert "greater than or equal to 1" in str(exc_info.value)

    def test_order_item_create_invalid_quantity(self):
        """Test OrderItemCreate with invalid quantity."""
        data = {
            "product_id": 1,
            "quantity": 0,  # Should be >= 1
            "price_at_purchase": 15.99
        }

        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(**data)

        assert "greater than or equal to 1" in str(exc_info.value)

    def test_order_item_create_invalid_price(self):
        """Test OrderItemCreate with invalid price."""
        data = {
            "product_id": 1,
            "quantity": 2,
            "price_at_purchase": 0  # Should be > 0
        }

        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(**data)

        assert "greater than 0" in str(exc_info.value)

    def test_order_item_response_complete(self):
        """Test OrderItemResponse with all fields."""
        data = {
            "product_id": 1,
            "quantity": 2,
            "price_at_purchase": 15.99,
            "order_item_id": 1,
            "order_id": 1,
            "item_total": 31.98,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 2, 12, 0, 0)
        }

        order_item = OrderItemResponse(**data)
        assert order_item.product_id == 1
        assert order_item.quantity == 2
        assert order_item.price_at_purchase == 15.99
        assert order_item.order_item_id == 1
        assert order_item.order_id == 1
        assert order_item.item_total == 31.98
        assert order_item.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert order_item.updated_at == datetime(2024, 1, 2, 12, 0, 0)


class TestOrderSchemas:
    """Unit tests for Order Pydantic schemas."""

    def test_order_create_valid(self):
        """Test creating a valid OrderCreate schema."""
        data = {
            "user_id": 1,
            "shipping_address": "123 Main St",
            "items": [
                {
                    "product_id": 1,
                    "quantity": 2,
                    "price_at_purchase": 15.99
                }
            ]
        }

        order = OrderCreate(**data)
        assert order.user_id == 1
        assert order.shipping_address == "123 Main St"
        assert len(order.items) == 1
        assert order.items[0].product_id == 1

    def test_order_create_default_status(self):
        """Test OrderCreate with default status."""
        data = {
            "user_id": 1,
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                    "price_at_purchase": 10.00
                }
            ]
        }

        order = OrderCreate(**data)
        assert order.status == "pending"

    def test_order_create_empty_items(self):
        """Test OrderCreate with empty items list - should pass schema validation."""
        data = {
            "user_id": 1,
            "items": []  # Schema allows empty items, endpoint will validate
        }

        # Should not raise ValidationError at schema level
        order = OrderCreate(**data)
        assert order.user_id == 1
        assert order.items == []

    def test_order_create_invalid_user_id(self):
        """Test OrderCreate with invalid user_id."""
        data = {
            "user_id": 0,  # Should be >= 1
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                    "price_at_purchase": 10.00
                }
            ]
        }

        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(**data)

        assert "greater than or equal to 1" in str(exc_info.value)

    def test_order_update_all_optional(self):
        """Test OrderUpdate with all fields optional."""
        # Should work with no fields provided
        order_update = OrderUpdate()
        assert order_update.user_id is None
        assert order_update.shipping_address is None
        assert order_update.status is None

    def test_order_update_partial(self):
        """Test OrderUpdate with partial data."""
        data = {
            "status": "shipped",
            "shipping_address": "456 Oak Ave"
        }

        order_update = OrderUpdate(**data)
        assert order_update.status == "shipped"
        assert order_update.shipping_address == "456 Oak Ave"
        assert order_update.user_id is None

    def test_order_response_complete(self):
        """Test OrderResponse with all fields."""
        data = {
            "user_id": 1,
            "shipping_address": "123 Main St",
            "status": "confirmed",
            "order_id": 1,
            "order_date": datetime(2024, 1, 1, 12, 0, 0),
            "total_amount": 25.99,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 2, 12, 0, 0),
            "items": []
        }

        order = OrderResponse(**data)
        assert order.user_id == 1
        assert order.shipping_address == "123 Main St"
        assert order.status == "confirmed"
        assert order.order_id == 1
        assert order.order_date == datetime(2024, 1, 1, 12, 0, 0)
        assert order.total_amount == 25.99
        assert order.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert order.updated_at == datetime(2024, 1, 2, 12, 0, 0)
        assert isinstance(order.items, list)

    def test_order_status_update_valid(self):
        """Test OrderStatusUpdate with valid status."""
        valid_statuses = [
            "pending", "processing", "shipped", "cancelled",
            "confirmed", "completed", "failed"
        ]

        for status in valid_statuses:
            data = {"status": status}
            status_update = OrderStatusUpdate(**data)
            assert status_update.status == status

    def test_order_status_update_invalid(self):
        """Test OrderStatusUpdate with invalid status."""
        data = {"status": "invalid_status"}

        with pytest.raises(ValidationError) as exc_info:
            OrderStatusUpdate(**data)

        assert "String should match pattern" in str(exc_info.value)

    def test_order_status_update_too_long(self):
        """Test OrderStatusUpdate with status too long."""
        data = {"status": "a" * 51}  # Exceeds 50 character limit

        with pytest.raises(ValidationError) as exc_info:
            OrderStatusUpdate(**data)

        assert "at most 50 characters" in str(exc_info.value)

    def test_order_shipping_address_too_long(self):
        """Test Order schemas with shipping address too long."""
        long_address = "x" * 1001  # Exceeds 1000 character limit

        # Test OrderCreate
        data = {
            "user_id": 1,
            "shipping_address": long_address,
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                    "price_at_purchase": 10.00
                }
            ]
        }

        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(**data)

        assert "at most 1000 characters" in str(exc_info.value)

        # Test OrderUpdate
        data = {"shipping_address": long_address}

        with pytest.raises(ValidationError) as exc_info:
            OrderUpdate(**data)

        assert "at most 1000 characters" in str(exc_info.value)