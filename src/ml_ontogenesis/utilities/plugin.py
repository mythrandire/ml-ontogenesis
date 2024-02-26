import abc
import importlib

from . import loghandler, properties


def get_subclass_map(class_type, class_map: dict) -> dict:
    """
    Recursively builds a map of all subclasses of a given class.

    Iterates through all subclasses of the specified `class_type`, including subclasses of subclasses,
    and adds them to a dictionary mapping the name of each subclass (as a string) to the subclass itself.
    This allows for easy lookup of subclasses by name.

    Parameters:
        - class_type: The parent class for which to find all subclasses.
        - class_map (dict)

        Returns:
        - dict: A dictionary mapping the names of all subclasses of `class_type` (and its subclasses recursively)
                to the subclass objects.

        Example:
        ```python
        class Animal:
            pass

        class Dog(Animal):
            pass

        class Cat(Animal):
            pass

        subclass_map = get_subclass_map(Animal, {})
        print(subclass_map)
        # Output: {'Dog': <class '__main__.Dog'>, 'Cat': <class '__main__.Cat'>}
        ```

        Note:
        The function modifies the `class_map` dictionary in place, but also returns it for
        convenience and chaining.
    """
    for subclass in class_type.__subclasses__():
        class_map[subclass.__name__] = subclass
        class_map = get_subclass_map(subclass, class_map)
    return class_map


class PluginBase(metaclass=abc.ABCMeta):
    """
    Abstract base class for creating a plugin system.

    This class provides a framework for registering, discovering, and instantiating plugins dynamically. It uses
    a class-level dictionary to maintain a registry of plugin subclasses, which can be accessed and manipulated
    through class methods. PluginBase is designed to be subclassed by specific plugin implementations, facilitating
    a flexible plugin architecture.

    Attributes:
        - _registered_plugins (dict): Class-level attribute to store registered plugins.
          This is initially None and is intended to be a dictionary where keys are plugin
          class names and values are the plugin classes themselves.

    Methods:
        - __init__(*args, **kwargs): Constructor for the PluginBase class. It allows for
          flexible instantiation but does not perform any action by itself.

    Class Methods:
        - add_registry(): Ensures the existence of the '_registered_plugins' dictionary
          at the class level.
        - has_registry(): Checks if the '_registered_plugins' dictionary exists at the
          class level.
        - has_registered_class(class_name): Checks if a given class name is registered
          in the plugin registry.
        - get_class(class_name, class_module=None, input_values=None): Retrieves a class
          from the registry or dynamically imports and returns it based on class name and
          optional module name.
        - gather_plugin_class_and_module_keywords(): Extracts plugin class and module
          names based on predefined class attributes or parameters.
        - extract_plugin_class_and_module_names(parameters, use_default): Extracts the
          class and module names for a plugin based on provided parameters or defaults.
        - lookup(class_name, class_module, input_values=None): Looks up and returns a
          registered subclass or dynamically loads one based on class name and optional
          module name.
        - construct(class_name, *args, class_module=None, **kwargs): Instantiates a plugin
          based on the class name and optional module name, passing any additional args
          and kwargs.
        - construct_from_parameters(parameters, *args, use_default=False, **kwargs):
          Instantiates a plugin based on parameters that specify the plugin class and
          optionally its module, passing any additional args and kwargs.
        - parse(class_name, *args, class_module=None, **kwargs): Similar to `construct`
          but specifically designed for plugins that can be initialized from a dictionary
          of parameters.
        - parse_from_parameters(parameters, *args, use_default=False, **kwargs): Similar
          to `construct_from_parameters` but for plugins that are initialized from a
          dictionary.

    Usage:
    PluginBase should not be instantiated directly but subclassed by specific plugin implementations. Subclasses may
    override methods as needed to provide specific functionality related to plugin discovery, loading, and
    instantiation.

    """
    _registered_plugins = None

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def add_registry(cls):
        if not hasattr(type(cls), '_registered_plugins'):
            setattr(type(cls), '_registered_plugins', dict())

    @classmethod
    def has_registry(cls):
        return hasattr(type(cls), '_registered_plugins')

    @classmethod
    def has_registered_class(cls, class_name):
        if not cls.has_registry():
            return False
        return class_name in type(cls)._registered_plugins

    @classmethod
    def get_class(cls, class_name, class_module=None, input_values=None):
        if not cls.has_registry():
            cls.add_registry()
        if cls.has_registered_class(class_name):
            return type(cls)._registered_plugins.get(class_name)
        else:
            subclasses = dict()
            subclasses = get_subclass_map(cls, subclasses)
            if class_name in subclasses:
                type(cls)._registered_plugins.update(**subclasses)
                return subclasses.get(class_name)
            else:
                if class_module is None and input_values is None:
                    return None
                elif class_module is None:
                    _, class_module = properties.ParsableProperty.get_class_and_module_strings(input_values,
                                                                                               parsable_class=class_name)
                if class_module is None:
                    return None
                imported_module = importlib.import_module(class_module)
                class_type = getattr(imported_module, class_name)
                subclasses = dict()
                subclasses = get_subclass_map(cls, subclasses)
                if class_type.__name__ in subclasses:
                    type(cls)._registered_plugins.update(**subclasses)
                return class_type

    @classmethod
    def gather_plugin_class_and_module_keywords(cls):
        if type(cls) is type(PluginBase):
            plugin_property_name = None
            plugin_module_property_name = None
            if hasattr(cls, 'parameters_cls'):
                if hasattr(cls.parameters_cls, 'plugin_property_name'):
                    plugin_property_name = cls.parameters_cls.plugin_property_name
                if hasattr(cls.parameters_cls, 'plugin_module_property_name'):
                    plugin_module_property_name = cls.parameters_cls.plugin_module_property_name
            else:
                if hasattr(cls, 'plugin_property_name'):
                    plugin_property_name = cls.plugin_property_name
                if hasattr(cls, 'plugin_module_property_name'):
                    plugin_module_property_name = cls.plugin_module_property_name
            return plugin_property_name, plugin_module_property_name
        else:
            raise RuntimeError(loghandler.error("Unable to deduce base class plugin properties in this class method "
                                                "when PluginBase is used as the base class. Try using a more specific base"
                                                " class implementation.", record_location=True))

    @classmethod
    def extract_plugin_class_and_module_names(cls, parameters, use_default):
        if use_default:
            plugin_property_name = properties.generic_parsable_type
            plugin_module_property_name = properties.generic_parsable_module
        else:
            plugin_property_name, plugin_module_property_name = cls.gather_plugin_class_and_module_keywords()
        if plugin_property_name is None:
            raise RuntimeError(loghandler.error("Unable to extract property to indicate the plugin type. Ensure"
                                                " that either the class contains a class variable named "
                                                "'plugin_property_name' which points to the property in the provided "
                                                "parameters object that indicates the plugin name or a class variable "
                                                "named 'parameters_cls' which points to the parameters class "
                                                "which then must contain a valid 'plugin_property_name' "
                                                "class variable. Unable to generate a plugin for class [",
                                                type(cls), "]!", record_location=True))
        if isinstance(parameters, dict):
            if plugin_property_name not in parameters:
                raise RuntimeError(loghandler.error("Unable to extract plugin property name [",
                                                    plugin_property_name,
                                                    "] from dict object. Unable to generate Plugin!",
                                                    record_location=True))
            else:
                class_name = parameters.get(plugin_property_name)

            if plugin_module_property_name is not None:
                if plugin_module_property_name not in parameters:
                    raise RuntimeError(loghandler.error("Unable to extract plugin module name [",
                                                        plugin_module_property_name,
                                                        "] from dict object. Unable to generate Plugin!",
                                                        record_location=True))
                else:
                    module_name = parameters.get(plugin_module_property_name)
            else:
                module_name = None
        else:
            if not hasattr(type(parameters), plugin_property_name):
                raise RuntimeError(loghandler.error("Unable to extract plugin property name [",
                                                    plugin_property_name, "] from parameters object [",
                                                    type(parameters), "]. Unable to generate Plugin!",
                                                    record_location=True))
            if hasattr(parameters, 'has_' + plugin_property_name):
                if getattr(parameters, 'has_' + plugin_property_name):
                    class_name = getattr(parameters, plugin_property_name)
                else:
                    raise RuntimeError(loghandler.error("The plugin property name [", plugin_property_name,
                                                        "] has not been assigned to the provided parameters object [",
                                                        type(parameters), "]. Unable to generate Plugin!",
                                                        record_location=True))
            else:
                class_name = getattr(parameters, plugin_property_name)

            if plugin_module_property_name is not None:
                if hasattr(parameters, 'has_' + plugin_module_property_name):
                    if getattr(parameters, 'has_' + plugin_module_property_name):
                        module_name = getattr(parameters, plugin_module_property_name)
                    else:
                        raise RuntimeError(loghandler.error("The plugin property name [", plugin_module_property_name,
                                                            "] has not been assigned to the provided parameters "
                                                            "object [",
                                                            type(parameters), "]. Unable to generate Plugin!",
                                                            record_location=True))
                else:
                    module_name = getattr(parameters, plugin_module_property_name)
            else:
                module_name = None

        return class_name, module_name

    @classmethod
    def lookup(cls, class_name, class_module, input_values=None):
        output_class = cls.get_class(class_name, class_module, input_values)
        if output_class is None:
            raise RuntimeError(loghandler.error("Subclass [", class_name, "] is not registered", record_location=True))
        return output_class

    @classmethod
    def construct(cls, class_name, *args, class_module=None, **kwargs):
        return cls.lookup(class_name, class_module, kwargs)(*args, **kwargs)

    @classmethod
    def construct_from_parameters(cls, parameters: object, *args: object, use_default: bool = False,
                                  **kwargs: object):
        class_name, module_name = cls.extract_plugin_class_and_module_names(parameters, use_default)
        return cls.construct(class_name, *args, class_module=module_name, **kwargs)

    @classmethod
    def parse(cls, class_name, *args, class_module=None, **kwargs):
        output_class = cls.lookup(class_name, class_module, kwargs)
        if hasattr(output_class, 'from_dict'):
            output_instance = output_class(*args)
            output_instance.from_dict(kwargs)
            return output_instance
        else:
            raise RuntimeError(loghandler.error("Class [", output_class.__name__,
                                                "] does not have a function named 'from_dict'", record_location=True))

    @classmethod
    def parse_from_parameters(cls, parameters, *args, use_default=False, **kwargs):
        class_name, module_name = cls.extract_plugin_class_and_module_names(parameters, use_default)
        return cls.parse(class_name, *args, class_module=module_name, **kwargs)
