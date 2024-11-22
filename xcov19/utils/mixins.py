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
    """Checks for correct signature used by the implementation class.

    Drop in mixin wherever an implementation is subclasses with an
    interface definition.
    """

    def __init_subclass__(cls, **kwargs):
        parent_class = inspect.getmro(cls)[1]
        # raise Exception(inspect.getmembers(cls, predicate=inspect.isfunction))
        for defined_method in (
            method_name
            for method_name, _ in inspect.getmembers(cls, predicate=inspect.isfunction)
            if not method_name.startswith("__")
        ):
            # Check if method is defined in parent class
            if not (
                hasattr(parent_class, defined_method)
                and (parent_cls_method := getattr(parent_class, defined_method))
            ):
                raise NotImplementedError(
                    f"Method {defined_method} must be implemented in class '{parent_class.__name__}'"
                )

            # No need to check if subclass method is defined since we are iterating over the subclass methods
            subclass_method = getattr(cls, defined_method)

            # Parent class implements the method, but subclass does not
            if parent_cls_method is subclass_method:
                raise NotImplementedError(
                    f"Subclass '{cls.__name__}' must override the method '{defined_method}' from the parent class '{parent_class.__name__}'."
                )

            parent_cls_method_params: dict = get_type_hints(parent_cls_method)
            subclass_method_params: dict = get_type_hints(subclass_method)
            if len(parent_cls_method_params) != len(subclass_method_params):
                raise NotImplementedError(f"""Method parameters mismatch:
                Expected: {parent_cls_method_params.keys()}
                Got: {subclass_method_params.keys()}
                """)
            for parent_cls_signature, subclass_signature in zip(
                parent_cls_method_params.items(), subclass_method_params.items()
            ):
                match_signature(parent_cls_signature, subclass_signature)
        super().__init_subclass__(**kwargs)
