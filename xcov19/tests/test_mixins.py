import pytest
from xcov19.utils.mixins import InterfaceProtocolCheckMixin


class BaseClass:
    def method_with_params(self, param1: int, param2: str):
        pass


# This class works correctly
class CorrectImplementation(BaseClass, InterfaceProtocolCheckMixin):
    def method_with_params(self, param1: int, param2: str):
        pass


def test_correct_implementation():
    # Should not raise any exception
    CorrectImplementation()


def test_missing_method_implementation():
    # Should raise NotImplementedError because method is missing
    with pytest.raises(NotImplementedError) as excinfo:
        # Define the class inline to trigger the __init_subclass__ check
        # Use the updated approach to see if the class definition itself raises the error
        type(
            "MissingMethodImplementation", (BaseClass, InterfaceProtocolCheckMixin), {}
        )
    assert "missing methods" in str(excinfo.value)
    assert "method_with_params" in str(excinfo.value)


def test_extra_method_implementation():
    # Should raise NotImplementedError because there's an extra method
    with pytest.raises(NotImplementedError) as excinfo:
        # Define the class inline to trigger the __init_subclass__ check
        class ExtraMethodImplementation(BaseClass, InterfaceProtocolCheckMixin):
            def method_with_params(self, param1: int, param2: str):
                pass

            def method2(self, param1: int):
                pass

    assert "methods not declared in interface" in str(excinfo.value)
    assert "method2" in str(excinfo.value)
