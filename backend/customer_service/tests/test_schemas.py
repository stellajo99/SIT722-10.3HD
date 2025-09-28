import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas import (
    CustomerBase, CustomerCreate, CustomerUpdate, CustomerResponse
)


class TestCustomerSchemas:
    """Unit tests for Customer Pydantic schemas."""

    def test_customer_create_valid(self):
        """Test creating a valid CustomerCreate schema."""
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+1234567890",
            "shipping_address": "123 Main St, City, State 12345",
            "password": "securepassword123"
        }

        customer = CustomerCreate(**data)
        assert customer.email == "test@example.com"
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.phone_number == "+1234567890"
        assert customer.shipping_address == "123 Main St, City, State 12345"
        assert customer.password == "securepassword123"

    def test_customer_create_minimal_valid(self):
        """Test creating a CustomerCreate with minimal required fields."""
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123"
        }

        customer = CustomerCreate(**data)
        assert customer.email == "test@example.com"
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.password == "securepassword123"
        assert customer.phone_number is None
        assert customer.shipping_address is None

    def test_customer_create_invalid_email(self):
        """Test CustomerCreate with invalid email."""
        data = {
            "email": "invalid-email",  # Invalid email format
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123"
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerCreate(**data)

        assert "value is not a valid email address" in str(exc_info.value)

    def test_customer_create_empty_first_name(self):
        """Test CustomerCreate with empty first name."""
        data = {
            "email": "test@example.com",
            "first_name": "",  # Should have min_length=1
            "last_name": "Doe",
            "password": "securepassword123"
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerCreate(**data)

        assert "at least 1 character" in str(exc_info.value)

    def test_customer_create_empty_last_name(self):
        """Test CustomerCreate with empty last name."""
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "",  # Should have min_length=1
            "password": "securepassword123"
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerCreate(**data)

        assert "at least 1 character" in str(exc_info.value)

    def test_customer_create_short_password(self):
        """Test CustomerCreate with short password."""
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "short"  # Should have min_length=8
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerCreate(**data)

        assert "at least 8 character" in str(exc_info.value)

    def test_customer_create_long_first_name(self):
        """Test CustomerCreate with first name exceeding max length."""
        data = {
            "email": "test@example.com",
            "first_name": "a" * 256,  # Should have max_length=255
            "last_name": "Doe",
            "password": "securepassword123"
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerCreate(**data)

        assert "at most 255 character" in str(exc_info.value)

    def test_customer_create_long_phone_number(self):
        """Test CustomerCreate with phone number exceeding max length."""
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "1" * 51,  # Should have max_length=50
            "password": "securepassword123"
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerCreate(**data)

        assert "at most 50 character" in str(exc_info.value)

    def test_customer_create_long_shipping_address(self):
        """Test CustomerCreate with shipping address exceeding max length."""
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "shipping_address": "a" * 1001,  # Should have max_length=1000
            "password": "securepassword123"
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerCreate(**data)

        assert "at most 1000 character" in str(exc_info.value)

    def test_customer_update_valid_partial(self):
        """Test CustomerUpdate with partial data (all fields optional)."""
        data = {
            "email": "updated@example.com",
            "first_name": "Jane"
        }

        customer = CustomerUpdate(**data)
        assert customer.email == "updated@example.com"
        assert customer.first_name == "Jane"
        assert customer.last_name is None
        assert customer.phone_number is None
        assert customer.shipping_address is None

    def test_customer_update_empty(self):
        """Test CustomerUpdate with no fields (all optional)."""
        data = {}

        customer = CustomerUpdate(**data)
        assert customer.email is None
        assert customer.first_name is None
        assert customer.last_name is None
        assert customer.phone_number is None
        assert customer.shipping_address is None

    def test_customer_update_invalid_email(self):
        """Test CustomerUpdate with invalid email."""
        data = {
            "email": "invalid-email"  # Invalid email format
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerUpdate(**data)

        assert "value is not a valid email address" in str(exc_info.value)

    def test_customer_update_empty_first_name(self):
        """Test CustomerUpdate with empty first name."""
        data = {
            "first_name": ""  # Should have min_length=1 if provided
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerUpdate(**data)

        assert "at least 1 character" in str(exc_info.value)

    def test_customer_response_valid(self):
        """Test CustomerResponse schema with valid data."""
        data = {
            "customer_id": 1,
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+1234567890",
            "shipping_address": "123 Main St",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        customer = CustomerResponse(**data)
        assert customer.customer_id == 1
        assert customer.email == "test@example.com"
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.phone_number == "+1234567890"
        assert customer.shipping_address == "123 Main St"
        assert isinstance(customer.created_at, datetime)
        assert isinstance(customer.updated_at, datetime)

    def test_customer_response_minimal(self):
        """Test CustomerResponse with minimal required fields."""
        data = {
            "customer_id": 1,
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "created_at": datetime.now()
        }

        customer = CustomerResponse(**data)
        assert customer.customer_id == 1
        assert customer.email == "test@example.com"
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert isinstance(customer.created_at, datetime)
        assert customer.phone_number is None
        assert customer.shipping_address is None
        assert customer.updated_at is None

    def test_customer_base_inheritance(self):
        """Test that CustomerCreate and CustomerResponse inherit from CustomerBase correctly."""
        # This test ensures the inheritance structure is working
        create_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123"
        }

        response_data = {
            "customer_id": 1,
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "created_at": datetime.now()
        }

        create_customer = CustomerCreate(**create_data)
        response_customer = CustomerResponse(**response_data)

        # Both should have the base fields
        assert create_customer.email == response_customer.email
        assert create_customer.first_name == response_customer.first_name
        assert create_customer.last_name == response_customer.last_name