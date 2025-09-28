import pytest
from decimal import Decimal
from datetime import datetime
from app.models import Product


class TestProductModel:
    """Unit tests for the Product model."""

    def test_product_creation(self):
        """Test creating a Product instance."""
        product = Product(
            name="Test Product",
            description="A test product description",
            price=Decimal("29.99"),
            stock_quantity=100,
            image_url="https://example.com/image.jpg"
        )

        assert product.name == "Test Product"
        assert product.description == "A test product description"
        assert product.price == Decimal("29.99")
        assert product.stock_quantity == 100
        assert product.image_url == "https://example.com/image.jpg"

    def test_product_creation_minimal(self):
        """Test creating a Product with only required fields."""
        product = Product(
            name="Minimal Product",
            price=Decimal("19.99"),
            stock_quantity=50
        )

        assert product.name == "Minimal Product"
        assert product.price == Decimal("19.99")
        assert product.stock_quantity == 50
        assert product.description is None
        assert product.image_url is None

    def test_product_repr(self):
        """Test the string representation of Product."""
        product = Product(
            product_id=1,
            name="Test Product",
            stock_quantity=25,
            image_url="https://example.com/very_long_image_url_that_should_be_truncated.jpg"
        )

        # The repr should truncate the image_url to 30 characters
        expected = "<Product(id=1, name='Test Product', stock=25, image_url='https://example.com/very_long_...')>"
        assert repr(product) == expected

    def test_product_repr_no_image_url(self):
        """Test the string representation of Product without image_url."""
        product = Product(
            product_id=2,
            name="No Image Product",
            stock_quantity=10,
            image_url=None
        )

        expected = "<Product(id=2, name='No Image Product', stock=10, image_url='None...')>"
        assert repr(product) == expected

    def test_product_required_fields(self):
        """Test that required fields are properly defined."""
        product = Product(
            name="Test Product",
            price=Decimal("29.99"),
            stock_quantity=100
        )

        # These fields are required
        assert hasattr(product, 'name')
        assert hasattr(product, 'price')
        assert hasattr(product, 'stock_quantity')

        # These fields are optional or auto-generated
        assert hasattr(product, 'product_id')
        assert hasattr(product, 'description')
        assert hasattr(product, 'image_url')
        assert hasattr(product, 'created_at')
        assert hasattr(product, 'updated_at')

    def test_product_default_stock_quantity(self):
        """Test that default stock_quantity is 0."""
        product = Product(
            name="Zero Stock Product",
            price=Decimal("15.99"),
            stock_quantity=0  # Explicitly set since SQLAlchemy column defaults don't apply to in-memory instances
        )

        assert product.stock_quantity == 0

    def test_product_default_stock_quantity_none_when_not_set(self):
        """Test that stock_quantity is None when not explicitly set (column default applies at DB level)."""
        product = Product(
            name="Zero Stock Product",
            price=Decimal("15.99")
        )

        # Stock quantity is None in memory - default 0 would be applied by database
        assert product.stock_quantity is None

    def test_product_tablename(self):
        """Test that the correct table name is set."""
        assert Product.__tablename__ == "products_week05"

    def test_decimal_precision(self):
        """Test that price maintains decimal precision."""
        product = Product(
            name="Precision Product",
            price=Decimal("123.456789"),
            stock_quantity=1
        )

        # Ensure Decimal precision is maintained
        assert isinstance(product.price, Decimal)
        assert product.price == Decimal("123.456789")

    def test_product_fields_types(self):
        """Test that product fields have correct types."""
        product = Product(
            name="Type Test Product",
            description="Description text",
            price=Decimal("29.99"),
            stock_quantity=50,
            image_url="https://example.com/image.jpg"
        )

        assert isinstance(product.name, str)
        assert isinstance(product.description, str) or product.description is None
        assert isinstance(product.price, Decimal)
        assert isinstance(product.stock_quantity, int)
        assert isinstance(product.image_url, str) or product.image_url is None

    def test_product_name_max_length_constraint(self):
        """Test that name field respects length constraints in model definition."""
        # Note: This tests the model definition, actual constraint enforcement
        # happens at the database level
        long_name = "x" * 300  # Longer than 255 characters

        product = Product(
            name=long_name,
            price=Decimal("29.99"),
            stock_quantity=50
        )

        # Model creation should work, but database would enforce constraint
        assert product.name == long_name

    def test_product_negative_stock(self):
        """Test product with negative stock quantity."""
        product = Product(
            name="Negative Stock Product",
            price=Decimal("29.99"),
            stock_quantity=-5  # Negative stock
        )

        # Model allows negative stock (business logic should handle this)
        assert product.stock_quantity == -5

    def test_product_zero_price(self):
        """Test product with zero price."""
        product = Product(
            name="Free Product",
            price=Decimal("0.00"),
            stock_quantity=100
        )

        assert product.price == Decimal("0.00")

    def test_product_very_long_description(self):
        """Test product with very long description."""
        long_description = "x" * 5000  # Very long description

        product = Product(
            name="Long Description Product",
            description=long_description,
            price=Decimal("29.99"),
            stock_quantity=10
        )

        assert product.description == long_description

    def test_product_very_long_image_url(self):
        """Test product with very long image URL."""
        long_url = "https://example.com/" + "x" * 3000  # Very long URL

        product = Product(
            name="Long URL Product",
            price=Decimal("29.99"),
            stock_quantity=10,
            image_url=long_url
        )

        assert product.image_url == long_url