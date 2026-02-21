import inspect
import operator
from typing import Tuple, Any, TypeVar, get_type_hints


ClassNameAttrGetter = operator.attrgetter("__name__")
BoundAttrGetter = operator.attrgetter("__bound__")


def match_signature(
    cls_signature: Tuple[str, Any], subclass_signature: Tuple[str, Any]
):
    """Match inspect signature by their names and type annotation."""
    param_name, param_type = cls_signature
    subcls_param_name, subcls_param_type = subclass_signature
    if param_name != subcls_param_name:
        raise NotImplementedError(
            f"""Method name mismatch:
                            Expected: {param_name}
                            Got: {subcls_param_name}
                            """
        )

    if ClassNameAttrGetter(param_type) != ClassNameAttrGetter(subcls_param_type):
        if (
            isinstance(param_type, TypeVar)
            and BoundAttrGetter(param_type) == subcls_param_type
        ):
            return True
        raise NotImplementedError(
            f"""
                            Signature mismatch for parameter {param_name}:
                            Expected: {param_type}
                            Got: {subcls_param_type}
                            """
        )
    return True


class InterfaceProtocolCheckMixin:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Identify the interface class (exclude the mixin itself)
        interfaces = [
            base for base in cls.__bases__
            if base is not InterfaceProtocolCheckMixin
        ]

        # If class does not implement an interface, skip checks
        if not interfaces:
            return

        # Usually only one interface
        interface = interfaces[0]

        # Collect all callable methods in the interface (ignore dunders)
        interface_methods = {
            name: func
            for name, func in interface.__dict__.items()
            if callable(func) and not name.startswith("__")
        }

        # Collect all callable methods in the implementation (ignore dunders)
        implementation_methods = {
            name: func
            for name, func in cls.__dict__.items()
            if callable(func) and not name.startswith("__")
        }

        # 1. Interface method missing in implementation
        for name, func in interface_methods.items():
            if name not in implementation_methods:
                raise NotImplementedError(
                    f"Class '{cls.__name__}' must implement method '{name}' "
                    f"declared in interface '{interface.__name__}'."
                )

            # Check method signatures
            sig_interface = inspect.signature(func)
            sig_impl = inspect.signature(implementation_methods[name])

            if sig_interface != sig_impl:
                raise NotImplementedError(
                    f"Signature mismatch for method '{name}'. "
                    f"Interface expects {sig_interface}, "
                    f"but implementation has {sig_impl}."
                )

        # 2. Extra methods in implementation not in interface
        for name in implementation_methods:
            if name not in interface_methods:
                raise NotImplementedError(
                    f"Method '{name}' is defined in '{cls.__name__}' "
                    f"but not declared in interface '{interface.__name__}'."
                )
