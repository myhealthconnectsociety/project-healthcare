import pytest

from xcov19.utils.mixins import InterfaceProtocolCheckMixin


# A base interface class with defined methods
class ParentInterface:
    def method_one(self, param: int) -> str:
        """Method one of Base Parent Interface Class"""
        raise NotImplementedError("Method one not implemented")

    def method_two(self, value: str) -> int:
        """Method two Base Parent Interface Class"""
        raise NotImplementedError("Method two not implemented")


def test_correct_implementation():
    # A correct subclass implementation
    class CorrectImplementation(ParentInterface, InterfaceProtocolCheckMixin):
        def method_one(self, param: int) -> str:
            return str(param)

        def method_two(self, value: str) -> int:
            return len(value)


def test_missing_methods():
    with pytest.raises(
        NotImplementedError,
        match="Subclass 'MissingMethodImplementation' must override the method 'method_two' from the parent class 'ParentInterface'.",
    ):
        # A subclass missing a required method
        class MissingMethodImplementation(ParentInterface, InterfaceProtocolCheckMixin):
            def method_one(self, param: int) -> str:
                return str(param)


def test_extra_methods():
    with pytest.raises(
        NotImplementedError,
        match="Method method_three must be implemented in class 'ParentInterface'",
    ):
        # A subclass with an extra method
        class ExtendedImplementation(ParentInterface, InterfaceProtocolCheckMixin):
            def method_one(self, param: int) -> str:
                return str(param)

            def method_two(self, value: str) -> int:
                return len(value)

            def method_three(self, extra: float) -> float:
                return extra * 2
