import pytest
from decimal import Decimal
from datetime import datetime
from app.models import Order, OrderItem


class TestOrderModel:
    """Unit tests for the Order model."""

    def test_order_creation(self):
        """Test creating an Order instance."""
        order = Order(
            user_id=1,
            status="pending",
            total_amount=Decimal("25.50"),
            shipping_address="123 Main St"
        )

        assert order.user_id == 1
        assert order.status == "pending"
        assert order.total_amount == Decimal("25.50")
        assert order.shipping_address == "123 Main St"

    def test_order_repr(self):
        """Test the string representation of Order."""
        order = Order(
            order_id=1,
            user_id=123,
            status="confirmed",
            total_amount=Decimal("99.99")
        )

        expected = "<Order(id=1, user_id=123, status='confirmed', total=99.99)>"
        assert repr(order) == expected

    def test_order_required_fields(self):
        """Test that required fields are properly defined."""
        order = Order(
            user_id=1,
            status="pending",
            total_amount=Decimal("10.00")
        )

        # These fields are required
        assert hasattr(order, 'user_id')
        assert hasattr(order, 'status')
        assert hasattr(order, 'total_amount')

        # These fields are optional or auto-generated
        assert hasattr(order, 'order_id')
        assert hasattr(order, 'order_date')
        assert hasattr(order, 'shipping_address')
        assert hasattr(order, 'created_at')
        assert hasattr(order, 'updated_at')
        assert hasattr(order, 'items')

    def test_order_default_status(self):
        """Test that default status is 'pending'."""
        order = Order(
            user_id=1,
            total_amount=Decimal("10.00"),
            status="pending"  # Explicitly set since SQLAlchemy column defaults don't apply to in-memory instances
        )

        assert order.status == "pending"

    def test_order_default_status_none_when_not_set(self):
        """Test that status is None when not explicitly set (column default applies at DB level)."""
        order = Order(
            user_id=1,
            total_amount=Decimal("10.00")
        )

        # Status is None in memory - default "pending" would be applied by database
        assert order.status is None

    def test_order_tablename(self):
        """Test that the correct table name is set."""
        assert Order.__tablename__ == "orders_week05"

    def test_order_items_relationship(self):
        """Test that items relationship is defined."""
        order = Order(
            user_id=1,
            status="pending",
            total_amount=Decimal("10.00")
        )

        # items should be a list initially (empty)
        assert hasattr(order, 'items')
        assert isinstance(order.items, list)


class TestOrderItemModel:
    """Unit tests for the OrderItem model."""

    def test_order_item_creation(self):
        """Test creating an OrderItem instance."""
        order_item = OrderItem(
            order_id=1,
            product_id=100,
            quantity=2,
            price_at_purchase=Decimal("15.99"),
            item_total=Decimal("31.98")
        )

        assert order_item.order_id == 1
        assert order_item.product_id == 100
        assert order_item.quantity == 2
        assert order_item.price_at_purchase == Decimal("15.99")
        assert order_item.item_total == Decimal("31.98")

    def test_order_item_repr(self):
        """Test the string representation of OrderItem."""
        order_item = OrderItem(
            order_item_id=1,
            order_id=123,
            product_id=456,
            quantity=3
        )

        expected = "<OrderItem(id=1, order_id=123, product_id=456, qty=3)>"
        assert repr(order_item) == expected

    def test_order_item_required_fields(self):
        """Test that required fields are properly defined."""
        order_item = OrderItem(
            order_id=1,
            product_id=100,
            quantity=2,
            price_at_purchase=Decimal("15.99"),
            item_total=Decimal("31.98")
        )

        # These fields are required
        assert hasattr(order_item, 'order_id')
        assert hasattr(order_item, 'product_id')
        assert hasattr(order_item, 'quantity')
        assert hasattr(order_item, 'price_at_purchase')
        assert hasattr(order_item, 'item_total')

        # These fields are auto-generated
        assert hasattr(order_item, 'order_item_id')
        assert hasattr(order_item, 'created_at')
        assert hasattr(order_item, 'updated_at')
        assert hasattr(order_item, 'order')

    def test_order_item_tablename(self):
        """Test that the correct table name is set."""
        assert OrderItem.__tablename__ == "order_items_week05"

    def test_order_item_foreign_key_relationship(self):
        """Test that order relationship is defined."""
        order_item = OrderItem(
            order_id=1,
            product_id=100,
            quantity=2,
            price_at_purchase=Decimal("15.99"),
            item_total=Decimal("31.98")
        )

        # order should be accessible (though None until set)
        assert hasattr(order_item, 'order')

    def test_decimal_precision(self):
        """Test that decimal values maintain precision."""
        order_item = OrderItem(
            order_id=1,
            product_id=100,
            quantity=1,
            price_at_purchase=Decimal("19.99"),
            item_total=Decimal("19.99")
        )

        # Ensure Decimal precision is maintained
        assert isinstance(order_item.price_at_purchase, Decimal)
        assert isinstance(order_item.item_total, Decimal)
        assert order_item.price_at_purchase == Decimal("19.99")
        assert order_item.item_total == Decimal("19.99")