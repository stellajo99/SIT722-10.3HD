import pytest
from datetime import datetime
from app.models import Customer


class TestCustomerModel:
    """Unit tests for the Customer model."""

    def test_customer_creation(self):
        """Test creating a Customer instance."""
        customer = Customer(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            phone_number="123-456-7890",
            shipping_address="123 Main St"
        )

        assert customer.email == "test@example.com"
        assert customer.password_hash == "hashed_password"
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.phone_number == "123-456-7890"
        assert customer.shipping_address == "123 Main St"

    def test_customer_repr(self):
        """Test the string representation of Customer."""
        customer = Customer(
            customer_id=1,
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe"
        )

        expected = "<Customer(id=1, email='test@example.com', name='John Doe')>"
        assert repr(customer) == expected

    def test_customer_required_fields(self):
        """Test that required fields are properly defined."""
        customer = Customer(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe"
        )

        # These fields are required
        assert hasattr(customer, 'email')
        assert hasattr(customer, 'password_hash')
        assert hasattr(customer, 'first_name')
        assert hasattr(customer, 'last_name')

        # These fields are optional
        assert hasattr(customer, 'phone_number')
        assert hasattr(customer, 'shipping_address')
        assert hasattr(customer, 'created_at')
        assert hasattr(customer, 'updated_at')

    def test_customer_optional_fields_default_none(self):
        """Test that optional fields can be None."""
        customer = Customer(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe"
        )

        # Optional fields should be None by default
        assert customer.phone_number is None
        assert customer.shipping_address is None

    def test_customer_tablename(self):
        """Test that the correct table name is set."""
        assert Customer.__tablename__ == "customers_week05"