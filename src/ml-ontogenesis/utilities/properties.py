import copy
from enum import Enum
from typing import List, Optional, Type, Union
import importlib
import inspect
import functools

from . import loghandler

generic_parsable_type = "parsable_type"
generic_parsable_module = "parsable_module"


def required_parameter_for_class_init(class_type) -> List[str]:
    required_args = set()
    signature = inspect.signature(class_type.__init__)
    for name, parameter in signature.parameters.items():
        if parameter.default == parameter.empty and parameter.name != "self" and parameter.kind not in (
                parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
            required_args.add(parameter.name)
    for base in class_type.__bases__:
        required_args = required_args.union(set(required_parameter_for_class_init(base)))
    return list(required_args)


def get_all_properties(obj, more_properties: dict) -> dict:
    more_properties.update(obj.__dict__)
    for b in obj.__bases__:
        more_properties = get_all_properties(b, more_properties)
    return more_properties


def is_property(obj, key):
    if not isinstance(obj, type):
        obj = type(obj)
    pro = get_all_properties(obj, dict()).get(key)
    return isinstance(pro, property)


def _get_property(obj, key):
    if not isinstance(obj, type):
        obj = type(obj)
    pro = get_all_properties(obj, dict()).get(key)
    if not isinstance(pro, property):
        raise RuntimeError(loghandler.error('{.__name__}.{} is not a property its a '.format(obj, key), type(pro),
                                            " and the object has ", get_all_properties(obj, dict())))
    return pro


def can_get(obj, key):
    return _get_property(obj, key).fget is not None


def can_set(obj, key):
    return _get_property(obj, key).fset is not None


def can_del(obj, key):
    return _get_property(obj, key).fdel is not None


class ParsableProperty(property):
    def __set__(self, obj, value):
        if isinstance(value, dict):
            value = ParsableProperty.parse(value)
        super(ParsableProperty, self).__set__(obj, value)

    def __get__(self, *args, **kwargs):  # real signature unknown
        return super(ParsableProperty, self).__get__(*args, **kwargs)

    @staticmethod
    def get_class_and_module_strings(input_value: dict,
                                     parsable_module=None,
                                     parsable_class=None,
                                     parsable_module_keyword=generic_parsable_module,
                                     parsable_class_keyword=generic_parsable_type,
                                     throw_if_unable_to_parse=False):

        module_str = None
        class_str = None
        # --- find the module to load ---
        if parsable_module is not None:
            if not isinstance(parsable_module, str):
                msg = loghandler.error("Unable to use type [", type(parsable_module),
                                       "] as a string-based name for loading the parsable module.",
                                       record_location=True)
                if throw_if_unable_to_parse:
                    raise RuntimeError(msg)
            else:
                module_str = parsable_module
        elif parsable_module_keyword in input_value:
            module_str = input_value[parsable_module_keyword]
        else:
            msg = loghandler.error("Unable to deduce the module name to load for parsing.", module_str,
                                   record_location=True)
            if throw_if_unable_to_parse:
                raise RuntimeError(msg)

        # --- find the class to load ---
        if parsable_class is not None:
            if not isinstance(parsable_class, str):
                msg = loghandler.error("Unable to use type [", type(parsable_class),
                                       "] as a string-based name for loading the parsable class.", record_location=True)
                if throw_if_unable_to_parse:
                    raise RuntimeError(msg)
            else:
                class_str = parsable_class
        elif parsable_class_keyword in input_value:
            class_str = input_value[parsable_class_keyword]
        else:
            msg = loghandler.error("Unable to deduce the class name to load for parsing.", record_location=True)
            if throw_if_unable_to_parse:
                raise RuntimeError(msg)

        return class_str, module_str

    @staticmethod
    def get_class_type(input_value: dict,
                       parsable_module=None,
                       parsable_class=None,
                       parsable_module_keyword=generic_parsable_module,
                       parsable_class_keyword=generic_parsable_type,
                       throw_if_unable_to_parse=False,
                       class_type=None):

        if class_type is None:
            class_str, module_str = ParsableProperty.get_class_and_module_strings(input_value,
                                                                                  parsable_module,
                                                                                  parsable_class,
                                                                                  parsable_module_keyword,
                                                                                  parsable_class_keyword,
                                                                                  throw_if_unable_to_parse)
            # --- load in the class ---
            if module_str is not None and class_str is not None:
                try:
                    imported_module = importlib.import_module(module_str)
                    class_type = getattr(imported_module, class_str)
                except BaseException as error:
                    msg = loghandler.error("Unable to construct parsable object [", class_str,
                                           "] in module [", module_str,
                                           "]. Encountered error: [", error, "]", record_location=True)
                    if throw_if_unable_to_parse:
                        raise RuntimeError(msg)
                    class_type = None

        return class_type

    @staticmethod
    def parse(input_value: dict,
              parsable_module=None,
              parsable_class=None,
              parsable_module_keyword=generic_parsable_module,
              parsable_class_keyword=generic_parsable_type,
              throw_if_unable_to_parse=False,
              class_type=None):

        class_type = ParsableProperty.get_class_type(input_value,
                                                     parsable_module,
                                                     parsable_class,
                                                     parsable_module_keyword,
                                                     parsable_class_keyword,
                                                     throw_if_unable_to_parse,
                                                     class_type)
        if class_type is not None:
            try:
                required_args = ParsableProperty.get_required_arguments_for_init(class_type, input_value)
                output = class_type(**required_args)
                output.from_dict(input_value)
                input_value = output
            except BaseException as error:
                msg = loghandler.error("Unable to construct parsable object [", class_type,
                                       "]. Encountered error: [", error, "]", record_location=True)
                if throw_if_unable_to_parse:
                    raise RuntimeError(msg)
        return input_value

    @staticmethod
    def get_required_arguments_for_init(class_type, input_dict: dict) -> dict:
        required_args = required_parameter_for_class_init(class_type)
        if not all(arg in input_dict for arg in required_args):
            raise RuntimeError(loghandler.error("The required arguments ", required_args,
                                                " are not included in the provided arguments ",
                                                list(input_dict.keys()), "."))
        return dict((k, input_dict[k]) for k in required_args)


def enum_parse(enum_type: Type[Enum],
               input_value: Union[str, int, List[Union[str, int]]]) -> Union[Optional[Enum], List[Enum]]:
    """Turns a string, integer, or list of strings or integers into the related enums based on the Enum type passed in.

    Args:
        enum_type: Type[Enum]
            A subclass type of Enum
        input_value: Union[str, int, List[Union[str, int]]]
            Either a string, integer, or list of string or integers

    Returns:
        Union[Optional[Enum], List[Enum]]
            Either the appropriate instance of the given enum type (or None), or a list of instances of given enum type

    Raises:
        TypeError:
            If the given input value cannot be converted to an enum instance, either:
                The int passed is not within the bounds of the enum
                The string passed does not correlate to an instance of the enum
                One of the items in the list passed does not correlate to an instance of the enum
                The type passed in can not be converted to an enum
    """
    if isinstance(input_value, list):
        return [enum_parse(enum_type, x) for x in input_value]
    if isinstance(input_value, enum_type) or input_value is None:
        return input_value
    elif isinstance(input_value, str):
        try:
            converted_value = enum_type[input_value]
        except KeyError:
            raise TypeError(
                loghandler.error(f"{input_value} is not a valid name of a {enum_type}", record_location=True))
    elif isinstance(input_value, int):
        try:
            converted_value = enum_type(input_value)
        except ValueError:
            raise TypeError(loghandler.error(f"Index {input_value} is not a valid index of a {enum_type}",
                                             record_location=True))
    else:
        raise TypeError(loghandler.error(f"{input_value} can not be converted to {enum_type}", record_location=True))

    return converted_value


# ---------------------------------------------------------------------------------------------------------------- #
# --- Decorators ------------------------------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------------------------------------------- #
def enum_setter(enum_type):
    def decorator_enum_setter(func):
        @functools.wraps(func)
        def wrapper_(self, input_value):
            converted_value = enum_parse(enum_type, input_value)
            func(self, converted_value)

        return wrapper_

    return decorator_enum_setter


def parsable_setter(parsable_module=None,
                    parsable_class=None,
                    parsable_module_keyword=generic_parsable_module,
                    parsable_class_keyword=generic_parsable_type,
                    throw_if_unable_to_parse=False,
                    class_type=None):
    def decorator_parsable_setter(func):
        @functools.wraps(func)
        def parsable_parse(self, input_value):
            if isinstance(input_value, dict):
                input_value = ParsableProperty.parse(input_value,
                                                     parsable_module,
                                                     parsable_class,
                                                     parsable_module_keyword,
                                                     parsable_class_keyword,
                                                     throw_if_unable_to_parse,
                                                     class_type)
            func(self, input_value)

        return parsable_parse

    return decorator_parsable_setter
