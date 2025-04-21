import pytest
from xcov19.utils.mixins import InterfaceProtocolCheckMixin


class BaseClass:
    """Base interface class for testing InterfaceProtocolCheckMixin."""

    def method_with_params(self, param1: int, param2: str) -> str:
        """Interface method with parameters that should be implemented by subclasses."""
        pass


# This class works correctly
class CorrectImplementation(BaseClass, InterfaceProtocolCheckMixin):
    """Implementation that correctly implements all methods from the BaseClass."""

    def method_with_params(self, param1: int, param2: str) -> str:
        """Correct implementation of the interface method."""
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

            def method_with_params(self, param1: int, param2: str) -> str:
                """Correct implementation of the required method."""
                pass

            def method2(self, param1: int):
                """Extra method not defined in the interface."""
                pass

    # Verify error message contains expected information
    assert "methods not declared in interface" in str(excinfo.value)
    assert "method2" in str(excinfo.value)


def test_incorrect_parameter_count():
    """Test that implementation with incorrect parameter count raises NotImplementedError."""
    with pytest.raises(NotImplementedError) as excinfo:
        # Define the class inline to trigger the __init_subclass__ check
        class IncorrectParameterCount(BaseClass, InterfaceProtocolCheckMixin):
            """Implementation with incorrect number of parameters."""

            def method_with_params(self, param1: int) -> str:
                """Implementation with incorrect parameter count."""
                pass

    # Verify error message contains expected information
    assert "parameters count mismatch" in str(excinfo.value)
    assert "method_with_params" in str(excinfo.value)


def test_incorrect_parameter_name():
    """Test that implementation with incorrect parameter name raises NotImplementedError."""
    with pytest.raises(NotImplementedError) as excinfo:
        # Define the class inline to trigger the __init_subclass__ check
        class IncorrectParameterName(BaseClass, InterfaceProtocolCheckMixin):
            """Implementation with incorrect parameter name."""

            def method_with_params(self, different_name: int, param2: str) -> str:
                """Implementation with incorrect parameter name."""
                pass

    # Verify error message contains expected information
    assert "Parameter name mismatch" in str(excinfo.value)
    assert "param1" in str(excinfo.value)
    assert "different_name" in str(excinfo.value)


def test_incorrect_parameter_type():
    """Test that implementation with incorrect parameter type raises NotImplementedError."""
    with pytest.raises(NotImplementedError) as excinfo:
        # Define the class inline to trigger the __init_subclass__ check
        class IncorrectParameterType(BaseClass, InterfaceProtocolCheckMixin):
            """Implementation with incorrect parameter type."""

            def method_with_params(self, param1: str, param2: str) -> str:
                """Implementation with incorrect parameter type."""
                pass

    # Verify error message contains expected information
    assert "Signature mismatch for parameter" in str(excinfo.value)
    assert "param1" in str(excinfo.value)


def test_incorrect_return_type():
    """Test that implementation with incorrect return type raises NotImplementedError."""
    with pytest.raises(NotImplementedError) as excinfo:
        # Define the class inline to trigger the __init_subclass__ check
        class IncorrectReturnType(BaseClass, InterfaceProtocolCheckMixin):
            """Implementation with incorrect return type."""

            def method_with_params(self, param1: int, param2: str) -> int:
                """Implementation with incorrect return type."""
                pass

    # Verify error message contains expected information
    assert "Signature mismatch for parameter return" in str(excinfo.value)
    assert "<class 'str'>" in str(excinfo.value)
    assert "<class 'int'>" in str(excinfo.value)
