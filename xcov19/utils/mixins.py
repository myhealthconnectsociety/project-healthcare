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


def _is_compatible_type(parent_type: Any, subclass_type: Any) -> bool:
    """Check if subclass_type is compatible with parent_type."""
    if parent_type == subclass_type:
        return True

    if isinstance(parent_type, TypeVar):
        if hasattr(parent_type, "__bound__") and parent_type.__bound__ is not None:
            return _is_compatible_type(parent_type.__bound__, subclass_type)
        return True

    if hasattr(parent_type, "__origin__") and hasattr(subclass_type, "__origin__"):
        if parent_type.__origin__ != subclass_type.__origin__:
            return False

        if hasattr(parent_type, "__args__") and hasattr(subclass_type, "__args__"):
            if len(parent_type.__args__) != len(subclass_type.__args__):
                return False

            for p_arg, s_arg in zip(parent_type.__args__, subclass_type.__args__):
                if not _is_compatible_type(p_arg, s_arg):
                    return False

            return True

    try:
        if issubclass(subclass_type, parent_type):
            return True
    except TypeError:
        pass

    return False


class InterfaceProtocolCheckMixin:
    """Checks for correct signature used by the implementation class.

    Drop in mixin wherever an implementation is subclasses with an
    interface definition.
    """

    def __init_subclass__(cls, **kwargs):
        parent_class = inspect.getmro(cls)[1]

        parent_methods = {name for name, attr in parent_class.__dict__.items()
                         if not name.startswith("__") and callable(attr)}

        cls_methods = {name for name, attr in cls.__dict__.items()
                      if not name.startswith("__") and callable(attr)}

        missing_in_impl = parent_methods - cls_methods
        if missing_in_impl:
            raise NotImplementedError(
                f"Implementation {cls.__name__} is missing methods declared in interface {parent_class.__name__}: {missing_in_impl}"
            )

        extra_in_impl = cls_methods - parent_methods
        if extra_in_impl:
            raise NotImplementedError(
                f"Implementation {cls.__name__} has methods not declared in interface {parent_class.__name__}: {extra_in_impl}"
            )

        for defined_method in cls_methods & parent_methods:
            parent_method = getattr(parent_class, defined_method)
            subclass_method = getattr(cls, defined_method)

            parent_sig = inspect.signature(parent_method)
            subclass_sig = inspect.signature(subclass_method)

            if len(parent_sig.parameters) != len(subclass_sig.parameters):
                raise NotImplementedError(
                    f"""Method parameters count mismatch for {defined_method}:
                Expected: {len(parent_sig.parameters)} parameters {list(parent_sig.parameters.keys())}
                Got: {len(subclass_sig.parameters)} parameters {list(subclass_sig.parameters.keys())}
                """
                )

            for (parent_param_name, parent_param), (subclass_param_name, subclass_param) in zip(
                parent_sig.parameters.items(), subclass_sig.parameters.items()
            ):
                if parent_param_name != subclass_param_name:
                    raise NotImplementedError(
                        f"""Parameter name mismatch in {defined_method}:
                    Expected: {parent_param_name}
                    Got: {subclass_param_name}
                    """
                    )

            parent_method_params: dict = get_type_hints(parent_method)
            subclass_method_params: dict = get_type_hints(subclass_method)

            for param_name, parent_type in parent_method_params.items():
                if param_name in subclass_method_params:
                    subclass_type = subclass_method_params[param_name]

                    if not _is_compatible_type(parent_type, subclass_type):
                        raise NotImplementedError(
                            f"""
                            Signature mismatch for parameter {param_name}:
                            Expected: {parent_type}
                            Got: {subclass_type}
                            """
                        )

        super().__init_subclass__(**kwargs)
