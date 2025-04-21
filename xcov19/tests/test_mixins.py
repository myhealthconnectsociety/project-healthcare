import pytest
from xcov19.utils.mixins import InterfaceProtocolCheckMixin


class BaseClass:
    """Base interface class for testing InterfaceProtocolCheckMixin."""

    def method_with_params(self, param1: int, param2: str):
        """
        Interface method with parameters that should be implemented by subclasses.
        This method is intentionally empty as it serves as an interface definition.
        """
        pass


# This class works correctly
class CorrectImplementation(BaseClass, InterfaceProtocolCheckMixin):
    """Implementation that correctly implements all methods from the BaseClass."""

    def method_with_params(self, param1: int, param2: str):
        """
        Correct implementation of the interface method.
        This implementation matches the signature from the base class.
        """
        pass


def test_correct_implementation():
    """Test that a correct implementation does not raise any exceptions."""
    instance = CorrectImplementation()
    # Verify the instance can be created without raising exceptions
    assert isinstance(instance, CorrectImplementation)
    # Verify the method can be called without errors
    instance.method_with_params(1, "test")


def test_missing_method_implementation():
    """Test that implementation missing a required method raises NotImplementedError."""
    with pytest.raises(NotImplementedError) as excinfo:
        # Define the class inline to trigger the __init_subclass__ check
        class MissingMethodImplementation(BaseClass, InterfaceProtocolCheckMixin):
            """Implementation that fails to implement the required method_with_params method."""

            pass

    # Verify error message contains expected information
    assert "missing methods" in str(excinfo.value)
    assert "method_with_params" in str(excinfo.value)


def test_extra_method_implementation():
    """Test that implementation with extra methods raises NotImplementedError."""
    with pytest.raises(NotImplementedError) as excinfo:
        # Define the class inline to trigger the __init_subclass__ check
        class ExtraMethodImplementation(BaseClass, InterfaceProtocolCheckMixin):
            """Implementation that adds an extra method not defined in the interface."""

            def method_with_params(self, param1: int, param2: str):
                """Correct implementation of the required method."""
                pass

            def method2(self, param1: int):
                """Extra method not defined in the interface."""
                pass

    # Verify error message contains expected information
    assert "methods not declared in interface" in str(excinfo.value)
    assert "method2" in str(excinfo.value)
