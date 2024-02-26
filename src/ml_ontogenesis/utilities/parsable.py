# --- external imports ---
from __future__ import annotations
from typing import List, Optional, Tuple, Union, Any, Sequence
from abc import abstractmethod, ABCMeta
import numpy as np
from pathlib import Path

from . import io, loghandler, properties


class Parsable(metaclass=ABCMeta):
    """
    A generic base class that enables serializing and deserializing internal information of subclasses.

    Inherits:
        abc.ABCMeta
    """

    def __init__(self, *args, **kwargs):
        pass

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Version Properties ----------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    @property
    @abstractmethod
    def has_version(self) -> bool:
        """Returns whether the version has been assigned."""
        pass  # pragma: no cover

    @property
    @abstractmethod
    def version(self) -> str:
        """Gets the version of this implementation of the Parsable class.

        Notes:
            The version should be incremented for every interface change made to an implementation of the
            Parsable class. This will allow tracking of parameter evolution with evolving data.

        Returns:
            str:
                The version number as a string.

        Raises:
            AttributeError:
                If the property has not been assigned yet.
        """
        pass  # pragma: no cover

    @version.setter
    @abstractmethod
    def version(self, input_value: Optional[str]):
        """Sets the version of this implementation of the Parsable class.

        Args:
            input_value: Optional[str]
                None or a string representation of the version.

        Raises:
            TypeError:
                If the provided `input_value` is not a supported type.
        """
        pass  # pragma: no cover

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Conversions ------------------------------------------------------------------------------------------------ #
    # ---------------------------------------------------------------------------------------------------------------- #
    @abstractmethod
    def to_dict(self) -> dict:
        """Serializes internal attributes into a JSON-compatible dictionary.

        Returns:
            dict
                A dictionary holding serializable keys that map to serialized representations of the values of
                internal attributes.
        """
        pass  # pragma: no cover

    @abstractmethod
    def from_dict(self, input_value: dict):
        """Populates the internal attributes from an input dictionary of serialized representation of values.

        Args:
            input_value: dict
                The serialized dictionary that is to be deserialized and used to hydrate the internal structures of this
                subclass implementation.
        """
        pass  # pragma: no cover

    @abstractmethod
    def update(self, only_if_missing: bool, input_value: dict):
        """Updates the internal attributes from the dictionary of the serialized representation of their values.

        Notes:
            This function differs from 'from_dict()' in that it allows for selective updating of the values depending
            on whether the attributes are already populated.

        Args:
            only_if_missing: bool
                If True then attributes whose values are not currently populated will be updated. If False, then
                the attributes will be updated regardless of their current status.
            input_value: dict
                The serialized dictionary that is to be deserialized and used to hydrate the internal structures of this
                subclass implementation.
        """
        pass  # pragma: no cover

    @abstractmethod
    def equals(self, other: Parsable, **kwargs) -> bool:
        """Compares whether two Parsable objects are equal in their parsable attributes.

        Args:
            other: Parsable
                The other Parsable to compare to this Parsable.
            **kwargs:
                Additional key-word arguments.

        Returns:
            bool:
                True iff all parsable attributes are equal.
        """
        pass  # pragma: no cover

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Serialization and IO --------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    def to_json(self, pickled: bool) -> Union[dict, str]:
        """
        Returns either the selectively serialized JSON object or the pickle-capable JSON version of this entire class.


        Args:
            pickled: bool
                If True then the entire class will be pickled into a JSON schema representation of this class. If false
                then the internal serialization routine will be performed.

        Returns:
            Union[dict, str]
                Either the dictionary of internally serialized attributes or the string of the serialized representation
                of the entire class.
        """
        if not pickled:
            return self.to_dict()
        return io.to_pickled_json(self)

    def from_json(self, json_object: Union[dict, str]):
        """Populates the internal attributes from a JSON based representation.

        Args:
            json_object: Union[dict, str]
                Either the serialized dictionary of this classes attributes or a string representation of a JSON
                document.
        """
        if isinstance(json_object, str):
            json_object = io.from_json_str(json_object)
        self.from_dict(json_object)

    @classmethod
    def from_pickled_json(cls, json_object: str):
        """Decodes a JSON string into a python class.

        Args:
            json_object: str
                The python string to decode.

        Returns:
            A Python object.
        """
        return io.from_pickled_json(json_object)

    def save_to_json(self, file_path: Union[str, Path], pickled: bool, **kwargs):
        """Saves the internal representation of this class to a desired file path.

        Args:
            file_path: Union[str, Path]
                A file path like object which must contain at least a directory in its value. Valid inputs take the form
                './foo/bar.baz' or '/foo/bar'.
            pickled: bool
                Indicates whether the entire class should be pickled. If False, then only the internal serialized
                attributes from this Parsable will be saved.
            **kwargs:
                Additional key-word arguments to provide to the JSON writer.

        Returns:
            Path
                The full Path object representing the location of the final output file.

        Raises:
            RuntimeError:
                If the provided 'file_path' is not formatted correctly.
        """
        # --- parse the file path ---
        path = io.to_path(file_path)
        if path.name == file_path:
            loghandler.log_and_raise(RuntimeError,"The input file_path [", file_path, "] does not contain a directory.")
        else:
            file_dir = path.parent

        # --- provide proper extension ---
        full_path = io.to_path(file_dir / path.name).with_suffix(".json")

        # --- make the directory ---
        io.create_directories(file_dir)

        # --- write the json file ---
        io.write_to_json_file(full_path, self.to_json(pickled), **kwargs)

        return full_path

    def load_from_json(self, file_path: Union[Path, str], **kwargs):
        """Loads and populates the internal attributes of this subclass from a JSON file.

        Args:
            file_path: Union[Path, str]
                The full path of the JSON file that is to be loaded.
            **kwargs:
                Additional key-word arguments to pass into the JSON reader.

        Raises:
            RuntimeError: If the provided 'file_path' does not point to file that currently exists.
        """
        # --- validate the file path ---
        if not io.file_exists(file_path):
            loghandler.log_and_raise(RuntimeError,"The file path [", file_path, "] does not exist. Cannot load object.")

        # --- read the json file ---
        json_object = io.read_json_file(file_path, **kwargs)

        # --- create the python object ---
        self.from_json(json_object)

    @classmethod
    def load_from_pickled_json(cls, file_path, **kwargs):
        """Loads a pickled JSON representation of a python class from file.

        Args:
            file_path: Union[Path, str]
                The full path of the JSON file that is to be loaded.
            **kwargs:
                Additional key-word arguments to pass into the JSON reader.

        Returns:
            A Python object.

        Raises:
            RuntimeError:
                If the provided 'file_path' does not point to file that currently exists.
        """
        # --- validate the file path ---
        if not io.file_exists(file_path):
            loghandler.log_and_raise(RuntimeError, "The file path [", file_path, "] does not exist. Cannot load object.")

        # --- read the json file ---
        json_object = io.read_json_file(file_path, **kwargs)

        # --- create the python object ---
        return cls.from_pickled_json(json_object)

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Conversions ------------------------------------------------------------------------------------------------ #
    # ---------------------------------------------------------------------------------------------------------------- #
    @classmethod
    def static_class_setter(cls):
        """A decorator function that provides the class module and name to the module loader routine.

        Examples:
            from package.utilities.parsable import Parsable

            class Foo(Parsable):
                def to_dict(self) -> dict:
                    return {}

                def from_dict(self, input_value: dict):
                    if 'foo' in input_value:
                        print("The foo is ", input_value['foo'])

                def update(self, only_if_missing: bool, input_value: dict):
                    pass

            class Bar:
                @property
                def bar(self):
                    return 'bar'

                @bar.setter
                @Foo.static_class_setter()
                def bar(self, input_value):
                    if not isinstance(input_value, Foo):
                        raise ValueError("Not a Foo!")

            bar = Bar()
            bar.bar = {'foo': 'baz'}

            Output:
            'The foo is baz'

        Returns:
            A python functor that can be place as a decorator for automatically parsing 'cls' without needing
            to provide the module or class name in the parsable dictionary.
        """
        return properties.parsable_setter(class_type=cls)


class GenericParsable(Parsable):
    """A class for generically parsing attributes of its eventual child class implementations."""

    def __init__(self, *args, **kwargs):
        super().__init__()
        # --- categories of parsable attributes ---
        self._serializable_attributes = []
        self._enum_attributes = []
        self._parsable_attributes = []
        self._specialized_attributes = []
        self._dict_of_parsables = []
        self._list_of_parsables = []

        # --- order of parsing ---
        self._desired_order_of_parsing = []

        # --- update the parsable attributes ---
        self._serializable_attributes.extend(['version'])

        # --- version ---
        self.version = kwargs.get('version')

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Version Properties ----------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    @property
    def has_version(self) -> bool:
        return self._version is not None

    @property
    def version(self) -> str:
        if self._version is None:
            loghandler.log_and_raise(AttributeError, "The version parameter has not been set.")
        return self._version

    @version.setter
    def version(self, input_value: Optional[bool]):
        if input_value is None or isinstance(input_value, str):
            self._version = input_value
        else:
            loghandler.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Parsing Order ---------------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    def collect_all_attributes(self) -> List[str]:
        """Returns a collective list of all registered attributes in no particular order."""
        output = list()
        output.extend(self._serializable_attributes)
        output.extend(self._enum_attributes)
        output.extend(self._parsable_attributes)
        output.extend(self._specialized_attributes)
        output.extend(self._dict_of_parsables)
        output.extend(self._list_of_parsables)
        return output

    def split_ordered_and_unordered_attributes(self) -> Tuple[List[str], List[str]]:
        """Splits the attributes between those that are to be parsed in a certain order and the rest of the attributes.

        Returns:
            Tuple[List[str], List[str]]
                The ordered and unordered attributes respectively.

        Raises:
            ValueError:
                If there are attributes registered in the '_desired_order_of_parsing' property that are not
                registered in any of the attributes categories.
        """
        # --- collect the attributes ---
        ordered_attributes = np.asanyarray(self._desired_order_of_parsing)
        all_attributes = np.asanyarray(self.collect_all_attributes())

        # --- trivial case ---
        if ordered_attributes.size == 0:
            return [], all_attributes.tolist()

        # --- ensure that all ordered attributes exist in the list of attributes ---
        exist = np.in1d(ordered_attributes, all_attributes)
        if not np.all(exist):
            missing_attributes = ordered_attributes[np.argwhere(np.logical_not(exist))]
            loghandler.log_and_raise(ValueError, "The desired ordered attributes [", missing_attributes,
                                 "] are missing from the registered attributes for class [",
                                 self.__class__.__name__, "].")

        # --- get the attributes that are not in the list of ordered attributes ---
        unordered_attributes = all_attributes[np.argwhere(np.logical_not(np.in1d(all_attributes, ordered_attributes)))]
        unordered_attributes = unordered_attributes.ravel()
        # --- return the ordered attributes and the unordered attributes ---
        return ordered_attributes.tolist(), unordered_attributes.tolist()

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Conversions ------------------------------------------------------------------------------------------------ #
    # ---------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def serialized_dict(input_value: dict) -> dict:
        """Converts a dictionary of serializable and parsable values into their serialized representation.

        Args:
            input_value: dict
                A dictionary of serializable keys mapping to objects that contain either a 'to_dict()' or 'tolist()'
                method. Values which do not contain one of these two methods are placed into the output dictionary
                as is.

        Returns:
            dict
                The serialized representation of the 'input_value'.
        """
        parsed_items = dict()
        for key, value in input_value.items():
            if hasattr(value, 'to_dict'):
                parsed_items[key] = value.to_dict()
            elif hasattr(value, 'tolist'):
                parsed_items[key] = value.tolist()
            else:
                parsed_items[key] = value
        return parsed_items

    @staticmethod
    def serialized_list(input_value: list) -> list:
        """Converts a list of serializable and parsable values into their serialized representation.

        Args:
            input_value: list
                A list of objects that contain either a 'to_dict()' or 'tolist()' method. Objects which do not contain
                one of these two methods are placed into the output list as is.

        Returns:
            list
                The serialized representation of the 'input_value'.
        """
        parsed_items = list()
        for item in input_value:
            if hasattr(item, 'to_dict'):
                parsed_items.append(item.to_dict())
            elif hasattr(item, 'tolist'):
                parsed_items.append(item.tolist())
            else:
                parsed_items.append(item)
        return parsed_items

    @staticmethod
    def parsed_dict(input_value: dict) -> dict:
        """Converts a dictionary of serializable and parsable values from their serialized representation.

        Args:
            input_value: dict
                A dictionary of serialized keys mapping to the serialized dictionary representation of Parsable
                subclasses. Vales that are not dictionaries or do not contain the key defined at
                'package.utilities.properties.generic_parsable_type' are placed into the output dictionary as is.

        Returns:
            dict
                The deserialized representation of the 'input_value'.
        """
        parsed_items = dict()
        for key, value in input_value.items():
            if isinstance(value, dict):
                if properties.generic_parsable_type in value:
                    parsed_items[key] = properties.ParsableProperty.parse(value, throw_if_unable_to_parse=True)
                else:
                    parsed_items[key] = value
            else:
                parsed_items[key] = value
        return parsed_items

    @staticmethod
    def parsed_list(input_value: list) -> list:
        """Converts a list of serializable and parsable values from their serialized representation.

        Args:
            input_value: list
                A list of serialized dictionary representation of Parsable subclasses. Objects that are not dictionaries
                or do not contain the key defined at 'package.utilities.properties.generic_parsable_type' are placed into
                the output list as is.

        Returns:
            list
                The deserialized representation of the 'input_value'.
        """
        parsed_items = list()
        for item in input_value:
            if isinstance(item, dict):
                if properties.generic_parsable_type in item:
                    parsed_items.append(properties.ParsableProperty.parse(item, throw_if_unable_to_parse=True))
                else:
                    parsed_items.append(item)
            else:
                parsed_items.append(item)
        return parsed_items

    def to_dict_serializable(self, output: dict, property_name: str):
        """Retrieves the serializable attribute and populates the output dictionary with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the serializable attribute to retrieve from this GenericParsable subclass.
        """
        if hasattr(self, "has_" + property_name):
            if self.__getattribute__("has_" + property_name):
                value = self.__getattribute__(property_name)
                if hasattr(value, 'tolist'):
                    value = value.tolist()
                if isinstance(value, frozenset):
                    value = list(value)
                output[property_name] = value
        else:
            value = self.__getattribute__(property_name)
            if hasattr(value, 'tolist'):
                value = value.tolist()
            if isinstance(value, frozenset):
                value = list(value)
            output[property_name] = value

    def to_dict_enum(self, output: dict, property_name: str):
        """Retrieves the enum attribute and populates the output dictionary with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the enum attribute to retrieve from this GenericParsable subclass.
        """
        if hasattr(self, "has_" + property_name):
            if self.__getattribute__("has_" + property_name):
                output[property_name] = self.__getattribute__(property_name).name
        else:
            output[property_name] = self.__getattribute__(property_name).name

    def to_dict_parsable(self, output: dict, property_name: str):
        """Retrieves the Parsable attribute and populates the output dictionary with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the Parsable attribute to retrieve from this GenericParsable subclass.
        """
        if hasattr(self, "has_" + property_name):
            if self.__getattribute__("has_" + property_name):
                output[property_name] = self.__getattribute__(property_name).to_dict()
        else:
            output[property_name] = self.__getattribute__(property_name).to_dict()

    def to_dict_dict_of_parsable(self, output: dict, property_name: str):
        """
        Retrieves the attribute whose value is a dictionary of Parsable objects and populates the output dictionary
        with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the attribute whose value is a dictionary of Parsable objects to retrieve from this
                GenericParsable subclass.
        """
        if hasattr(self, "has_" + property_name):
            if self.__getattribute__("has_" + property_name):
                item = self.__getattribute__(property_name)
                if isinstance(item, dict):
                    output[property_name] = GenericParsable.serialized_dict(item)
        else:
            item = self.__getattribute__(property_name)
            if isinstance(item, dict):
                output[property_name] = GenericParsable.serialized_dict(item)

    def to_dict_list_of_parsable(self, output: dict, property_name: str):
        """
        Retrieves the attribute whose value is a list of Parsable objects and populates the output dictionary
        with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the attribute whose value is a list of Parsable objects to retrieve from this
                GenericParsable subclass.
        """
        if hasattr(self, "has_" + property_name):
            if self.__getattribute__("has_" + property_name):
                item = self.__getattribute__(property_name)
                if isinstance(item, (Sequence, set, frozenset)):
                    output[property_name] = GenericParsable.serialized_list(list(item))

        else:
            item = self.__getattribute__(property_name)
            if isinstance(item, (Sequence, set, frozenset)):
                output[property_name] = GenericParsable.serialized_list(list(item))

    def to_dict_specialized(self, output: dict, property_name: str):
        """
        Retrieves the attribute whose value is requires a specialized encoding function and populates the output
        dictionary with its serialized representation.

        Args:
            output: dict
                The output dictionary of serialized attributes for which to modify inplace.
            property_name: str
                The name of the attribute to retrieve from this GenericParsable subclass. This subclass must have
                a method named ''property_name'_encode'. For example for a property_name = 'foo', a method should exist
                named 'foo_encode'.

        Raises:
            AttributeError: If the GenericParsable subclass does not have a method named ''property_name'_encode'.
        """
        if hasattr(self, property_name + '_encode'):
            if hasattr(self, "has_" + property_name):
                if self.__getattribute__("has_" + property_name):
                    output[property_name] = self.__getattribute__(property_name + '_encode')()
            else:
                output[property_name] = self.__getattribute__(property_name + '_encode')()
        else:
            loghandler.log_and_raise(AttributeError, "Unable to construct attribute [", property_name,
                                 "] since there is no function [", property_name + '_encode', "].")

    def to_dict(self) -> dict:
        output = dict()
        output[properties.generic_parsable_type] = self.__class__.__name__
        output[properties.generic_parsable_module] = self.__class__.__module__

        # --- serializable ---
        for property_name in self._serializable_attributes:
            self.to_dict_serializable(output, property_name)

        # --- enums ---
        for property_name in self._enum_attributes:
            self.to_dict_enum(output, property_name)

        # --- parsable ---
        for property_name in self._parsable_attributes:
            self.to_dict_parsable(output, property_name)

        # --- dict of parsables ---
        for property_name in self._dict_of_parsables:
            self.to_dict_dict_of_parsable(output, property_name)

        # --- list of parsables ---
        for property_name in self._list_of_parsables:
            self.to_dict_list_of_parsable(output, property_name)

        # --- specialized ---
        for property_name in self._specialized_attributes:
            self.to_dict_specialized(output, property_name)
        return output

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- De-serialize from a dict ----------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    def from_dict_serializable(self, input_value: dict, property_name: str):
        """Retrieves the serializable value from the input dictionary and populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the serializable attribute to populate. This attribute is only populated if the
                'property_name' is settable and is in the 'input_value'.
        """
        if property_name in input_value:
            if properties.can_set(self, property_name):
                self.__setattr__(property_name, input_value.get(property_name))

    def from_dict_enum(self, input_value: dict, property_name: str):
        """Retrieves the enum value from the input dictionary and populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the enum attribute to populate. This attribute is only populated if the
                'property_name' is settable and is in the 'input_value'. Attributes must have an @enum_setter()
                decorator on the property setter functions.
        """
        self.from_dict_serializable(input_value, property_name)

    def from_dict_parsable(self, input_value: dict, property_name: str):
        """Retrieves the Parsable value from the input dictionary and populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the Parsable attribute to populate. This attribute is only populated if the
                'property_name' is settable and is in the 'input_value'. Attributes must have a @parsable_setter()
                decorator on the property setter functions or be able to parse the input value within the setter.
        """
        self.from_dict_serializable(input_value, property_name)

    def from_dict_dict_of_parsable(self, input_value: dict, property_name: str):
        """
        Retrieves the attribute whose value is a dictionary of Parsable objects from the input dictionary and
        populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute whose value is a dictionary of Parsable objects to populate. This
                attribute is only populated if the 'property_name' is settable and is in the 'input_value'.
        """
        if property_name in input_value:
            if properties.can_set(self, property_name):
                value = input_value.get(property_name)
                if isinstance(value, dict):
                    value = GenericParsable.parsed_dict(value)
                self.__setattr__(property_name, value)

    def from_dict_list_of_parsable(self, input_value: dict, property_name: str):
        """
        Retrieves the attribute whose value is a list of Parsable objects from the input dictionary and
        populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute whose value is a list of Parsable objects to populate. This
                attribute is only populated if the 'property_name' is settable and is in the 'input_value'.
        """
        if property_name in input_value:
            if properties.can_set(self, property_name):
                value = input_value.get(property_name)
                if isinstance(value, list):
                    value = GenericParsable.parsed_list(value)
                self.__setattr__(property_name, value)

    def from_dict_specialized(self, input_value: dict, property_name: str):
        """
        Retrieves the attribute whose value is requires a specialized decoding function from the input dictionary
        and populates the desired attribute.

        Args:
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate. This attribute is only populated if the 'property_name' is
                settable and is in the 'input_value'. This subclass must have a method named ''property_name'_decode'.
                For example for a property_name = 'foo', a method should exist named 'foo_decode'.

        Raises:
            AttributeError: If the GenericParsable subclass does not have a method named ''property_name'_decode'.
        """
        if property_name in input_value:
            if hasattr(self, property_name + '_decode'):
                self.__getattribute__(property_name + '_decode')(input_value.get(property_name))
            else:
                loghandler.log_and_raise(AttributeError, "Unable to decode attribute [", property_name,
                                     "] since there is no function [", property_name + '_decode', "].")

    def from_dict(self, input_value: dict):
        ordered_attributes, unordered_attributes = self.split_ordered_and_unordered_attributes()
        for property_name in (*ordered_attributes, *unordered_attributes):
            if property_name in self._serializable_attributes:
                self.from_dict_serializable(input_value, property_name)
            elif property_name in self._parsable_attributes:
                self.from_dict_parsable(input_value, property_name)
            elif property_name in self._enum_attributes:
                self.from_dict_enum(input_value, property_name)
            elif property_name in self._dict_of_parsables:
                self.from_dict_dict_of_parsable(input_value, property_name)
            elif property_name in self._list_of_parsables:
                self.from_dict_list_of_parsable(input_value, property_name)
            elif property_name in self._specialized_attributes:
                self.from_dict_specialized(input_value, property_name)
            else:
                loghandler.log_and_raise(RuntimeError, "The property [", property_name, "] doesn't exist!")

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Update by de-serializing from a dict ----------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    def update_property(self, input_value: Any, property_name: str):
        """Updates a property of this class.

        Args:
            input_value: Any
                A value of any kind with which the property will be updated.
            property_name: str
                The name of the attribute to populate.
        """
        if hasattr(self, name := "update_" + property_name) and callable(updater := getattr(self, name)):
            updater(input_value)
        elif properties.can_set(self, property_name):
            self.__setattr__(property_name, input_value)
        else:
            loghandler.debug("Unable to update property [", property_name, "].", record_location=True)

    def update_serializable_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """Retrieves the serializable value from the input dictionary and populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.
        """
        if only_if_missing:
            if hasattr(self, "has_" + property_name):
                if self.__getattribute__("has_" + property_name):
                    return
        if property_name in input_value:
            self.update_property(input_value.get(property_name), property_name)

    def update_enum_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """Retrieves the enum value from the input dictionary and populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.
        """
        self.update_serializable_property(only_if_missing, input_value, property_name)

    def update_parsable_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """Retrieves the Parsable value from the input dictionary and populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.
        """
        self.update_serializable_property(only_if_missing, input_value, property_name)

    def update_dict_of_parsable_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """Retrieves the attribute whose value is a dictionary of Parsable objects from the input dictionary and
        populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.
        """
        if only_if_missing:
            if hasattr(self, "has_" + property_name):
                if self.__getattribute__("has_" + property_name):
                    return
        if property_name in input_value:
            value = input_value.get(property_name)
            if isinstance(value, dict):
                value = GenericParsable.parsed_dict(value)
            self.update_property(value, property_name)

    def update_list_of_parsable_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """
        Retrieves the attribute whose value is a list of Parsable objects from the input dictionary and
        populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.
        """
        if only_if_missing:
            if hasattr(self, "has_" + property_name):
                if self.__getattribute__("has_" + property_name):
                    return
        if property_name in input_value:
            value = input_value.get(property_name)
            if isinstance(value, list):
                value = GenericParsable.parsed_list(value)
            self.update_property(value, property_name)

    def update_specialized_property(self, only_if_missing: bool, input_value: dict, property_name: str):
        """
        Retrieves the attribute whose value is requires a specialized decoding function from the input dictionary
        and populates the desired attribute if desired.

        Args:
            only_if_missing: bool
                Indicates whether the attribute should be updated only if it does not currently have a value assigned.
            input_value: dict
                The input dictionary of serialized attributes in which to deserialize.
            property_name: str
                The name of the attribute to populate.

        Raises:
            AttributeError: If the GenericParsable subclass does not have a method named ''property_name'_decode'.
        """
        if hasattr(self, property_name + '_decode'):
            if only_if_missing:
                if hasattr(self, "has_" + property_name):
                    if self.__getattribute__("has_" + property_name):
                        return
            if property_name in input_value:
                self.__getattribute__(property_name + '_decode')(input_value.get(property_name))
        else:
            loghandler.log_and_raise(AttributeError, "Unable to decode attribute [", property_name,
                                 "] since there is no function [", property_name + '_decode', "].")

    def update(self, only_if_missing: bool, input_value: dict):
        ordered_attributes, unordered_attributes = self.split_ordered_and_unordered_attributes()

        for property_name in (*ordered_attributes, *unordered_attributes):
            if property_name in self._serializable_attributes:
                self.update_serializable_property(only_if_missing, input_value, property_name)
            elif property_name in self._parsable_attributes:
                self.update_parsable_property(only_if_missing, input_value, property_name)
            elif property_name in self._enum_attributes:
                self.update_enum_property(only_if_missing, input_value, property_name)
            elif property_name in self._dict_of_parsables:
                self.update_dict_of_parsable_property(only_if_missing, input_value, property_name)
            elif property_name in self._list_of_parsables:
                self.update_list_of_parsable_property(only_if_missing, input_value, property_name)
            elif property_name in self._specialized_attributes:
                self.update_specialized_property(only_if_missing, input_value, property_name)
            else:
                loghandler.log_and_raise(RuntimeError, "The property [", property_name, "] doesn't exist!")

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Equality --------------------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #

    def equals(self, other: GenericParsable, **kwargs) -> bool:
        """Returns if all parsable attributes of other GenericParsable are equal to self.

        Args:
            other: GenericParsable
                The object to compare with self.

        Returns:
            bool:
                If the two parsables are equal.
        """
        if type(self) != type(other):
            return False

        for property_name in self._serializable_attributes:
            self_value, other_value, equals = self.equals_property_name(other, property_name)
            if equals:
                continue
            elif equals is False or not equal(self_value, other_value, **kwargs):
                return False

        for property_name in self._enum_attributes:
            self_value, other_value, equals = self.equals_property_name(other, property_name)
            if equals:
                continue
            elif equals is False or not equal(self_value, other_value, **kwargs):
                return False

        for property_name in self._parsable_attributes:
            self_value, other_value, equals = self.equals_property_name(other, property_name)
            if equals:
                continue
            elif equals is False or not equal(self_value, other_value, **kwargs):
                return False

        for property_name in self._dict_of_parsables:
            self_value, other_value, equals = self.equals_property_name(other, property_name)
            if equals:
                continue
            elif equals is False or not equal(self_value, other_value, **kwargs):
                return False

        for property_name in self._list_of_parsables:
            self_value, other_value, equals = self.equals_property_name(other, property_name)
            if equals:
                continue
            elif equals is False or not equal(self_value, other_value, **kwargs):
                return False

        for property_name in self._specialized_attributes:
            self_value, other_value, equals = self.equals_property_name(other, property_name)
            if equals:
                continue
            elif equals is False or not equal(self_value, other_value, **kwargs):
                return False

        return True

    def equals_property_name(self, other: GenericParsable, property_name: str) -> Tuple[Any, Any, Optional[bool]]:
        """Check if self and other have a property and get the property if they do.

        Args:
            other: GenericParsable
                Another GenericParsable of the same type as self.
            property_name: str
                The name of the property to check.

        Returns:
            Tuple[Any, Any, Optional[bool]]
                The value of the properties from self + other (if both Parsables had the property) and if we can short
                circuit the evaluation. If the third item in the tuple is not None, we don't need to compare the values.
        """
        if hasattr(self, 'has_' + property_name):
            self_has_property = self.__getattribute__('has_' + property_name)
            other_has_property = other.__getattribute__('has_' + property_name)
            if not self_has_property and not other_has_property:
                return None, None, True
            elif self_has_property != other_has_property:
                return None, None, False

        self_value = self.__getattribute__(property_name)
        other_value = other.__getattribute__(property_name)
        if type(self_value) != type(other_value):
            return None, None, False

        return self_value, other_value, None
