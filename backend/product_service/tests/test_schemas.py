import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas import ProductCreate, ProductUpdate, ProductResponse, StockDeductRequest


class TestProductSchemas:
    """Unit tests for Product Pydantic schemas."""

    def test_product_create_valid(self):
        """Test creating a valid ProductCreate schema."""
        data = {
            "name": "Test Product",
            "description": "A test product",
            "price": 29.99,
            "stock_quantity": 100,
            "image_url": "https://example.com/image.jpg"
        }

        product = ProductCreate(**data)
        assert product.name == "Test Product"
        assert product.description == "A test product"
        assert product.price == 29.99
        assert product.stock_quantity == 100
        assert product.image_url == "https://example.com/image.jpg"

    def test_product_create_minimal_required_fields(self):
        """Test ProductCreate with only required fields."""
        data = {
            "name": "Minimal Product",
            "price": 19.99,
            "stock_quantity": 50
        }

        product = ProductCreate(**data)
        assert product.name == "Minimal Product"
        assert product.price == 19.99
        assert product.stock_quantity == 50
        assert product.description is None
        assert product.image_url is None

    def test_product_create_invalid_price_zero(self):
        """Test ProductCreate with zero price (invalid)."""
        data = {
            "name": "Invalid Product",
            "price": 0.0,  # Should be > 0
            "stock_quantity": 50
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert "greater than 0" in str(exc_info.value)

    def test_product_create_invalid_price_negative(self):
        """Test ProductCreate with negative price (invalid)."""
        data = {
            "name": "Invalid Product",
            "price": -10.0,  # Should be > 0
            "stock_quantity": 50
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert "greater than 0" in str(exc_info.value)

    def test_product_create_invalid_stock_negative(self):
        """Test ProductCreate with negative stock quantity (invalid)."""
        data = {
            "name": "Invalid Product",
            "price": 29.99,
            "stock_quantity": -1  # Should be >= 0
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert "greater than or equal to 0" in str(exc_info.value)

    def test_product_create_valid_zero_stock(self):
        """Test ProductCreate with zero stock quantity (valid)."""
        data = {
            "name": "Zero Stock Product",
            "price": 29.99,
            "stock_quantity": 0  # Valid
        }

        product = ProductCreate(**data)
        assert product.stock_quantity == 0

    def test_product_create_empty_name(self):
        """Test ProductCreate with empty name (invalid)."""
        data = {
            "name": "",  # Should be at least 1 character
            "price": 29.99,
            "stock_quantity": 50
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert "at least 1 character" in str(exc_info.value)

    def test_product_create_long_name(self):
        """Test ProductCreate with name exceeding max length."""
        data = {
            "name": "x" * 256,  # Exceeds 255 character limit
            "price": 29.99,
            "stock_quantity": 50
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert "at most 255 characters" in str(exc_info.value)

    def test_product_create_long_description(self):
        """Test ProductCreate with description exceeding max length."""
        data = {
            "name": "Test Product",
            "description": "x" * 2001,  # Exceeds 2000 character limit
            "price": 29.99,
            "stock_quantity": 50
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert "at most 2000 characters" in str(exc_info.value)

    def test_product_create_long_image_url(self):
        """Test ProductCreate with image URL exceeding max length."""
        data = {
            "name": "Test Product",
            "price": 29.99,
            "stock_quantity": 50,
            "image_url": "https://example.com/" + "x" * 2048  # Exceeds 2048 character limit
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**data)

        assert "at most 2048 characters" in str(exc_info.value)

    def test_product_update_all_optional(self):
        """Test ProductUpdate with all fields optional."""
        # Should work with no fields provided
        product_update = ProductUpdate()
        assert product_update.name is None
        assert product_update.description is None
        assert product_update.price is None
        assert product_update.stock_quantity is None
        assert product_update.image_url is None

    def test_product_update_partial(self):
        """Test ProductUpdate with partial data."""
        data = {
            "name": "Updated Product",
            "price": 39.99
        }

        product_update = ProductUpdate(**data)
        assert product_update.name == "Updated Product"
        assert product_update.price == 39.99
        assert product_update.description is None
        assert product_update.stock_quantity is None
        assert product_update.image_url is None

    def test_product_update_invalid_price(self):
        """Test ProductUpdate with invalid price."""
        data = {
            "price": 0.0  # Should be > 0
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductUpdate(**data)

        assert "greater than 0" in str(exc_info.value)

    def test_product_update_invalid_stock(self):
        """Test ProductUpdate with invalid stock quantity."""
        data = {
            "stock_quantity": -5  # Should be >= 0
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductUpdate(**data)

        assert "greater than or equal to 0" in str(exc_info.value)

    def test_product_response_complete(self):
        """Test ProductResponse with all fields."""
        data = {
            "name": "Response Product",
            "description": "A response product",
            "price": 29.99,
            "stock_quantity": 100,
            "image_url": "https://example.com/image.jpg",
            "product_id": 1,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 2, 12, 0, 0)
        }

        product = ProductResponse(**data)
        assert product.name == "Response Product"
        assert product.description == "A response product"
        assert product.price == 29.99
        assert product.stock_quantity == 100
        assert product.image_url == "https://example.com/image.jpg"
        assert product.product_id == 1
        assert product.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert product.updated_at == datetime(2024, 1, 2, 12, 0, 0)

    def test_product_response_minimal(self):
        """Test ProductResponse with minimal required fields."""
        data = {
            "name": "Minimal Response Product",
            "price": 19.99,
            "stock_quantity": 50,
            "product_id": 1,
            "created_at": datetime(2024, 1, 1, 12, 0, 0)
        }

        product = ProductResponse(**data)
        assert product.name == "Minimal Response Product"
        assert product.price == 19.99
        assert product.stock_quantity == 50
        assert product.product_id == 1
        assert product.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert product.description is None
        assert product.image_url is None
        assert product.updated_at is None

    def test_product_response_missing_required_field(self):
        """Test ProductResponse missing required field."""
        data = {
            "name": "Missing ID Product",
            "price": 19.99,
            "stock_quantity": 50,
            "created_at": datetime(2024, 1, 1, 12, 0, 0)
            # Missing product_id which is required
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductResponse(**data)

        assert "product_id" in str(exc_info.value)


class TestStockDeductRequest:
    """Unit tests for StockDeductRequest schema."""

    def test_stock_deduct_request_valid(self):
        """Test creating a valid StockDeductRequest."""
        data = {
            "quantity_to_deduct": 5
        }

        request = StockDeductRequest(**data)
        assert request.quantity_to_deduct == 5

    def test_stock_deduct_request_invalid_zero(self):
        """Test StockDeductRequest with zero quantity (invalid)."""
        data = {
            "quantity_to_deduct": 0  # Should be > 0
        }

        with pytest.raises(ValidationError) as exc_info:
            StockDeductRequest(**data)

        assert "greater than 0" in str(exc_info.value)

    def test_stock_deduct_request_invalid_negative(self):
        """Test StockDeductRequest with negative quantity (invalid)."""
        data = {
            "quantity_to_deduct": -3  # Should be > 0
        }

        with pytest.raises(ValidationError) as exc_info:
            StockDeductRequest(**data)

        assert "greater than 0" in str(exc_info.value)

    def test_stock_deduct_request_large_quantity(self):
        """Test StockDeductRequest with large quantity."""
        data = {
            "quantity_to_deduct": 1000000
        }

        request = StockDeductRequest(**data)
        assert request.quantity_to_deduct == 1000000

    def test_stock_deduct_request_missing_field(self):
        """Test StockDeductRequest with missing required field."""
        data = {}  # Missing quantity_to_deduct

        with pytest.raises(ValidationError) as exc_info:
            StockDeductRequest(**data)

        assert "quantity_to_deduct" in str(exc_info.value)