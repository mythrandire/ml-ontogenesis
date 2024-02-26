import copy
from typing import Union, Any, Optional

from . import loghandler, io, parsable, plugin


class ParametersBase(parsable.GenericParsable, plugin.PluginBase):
    """
    Represents the base class for all configurable input parameters.
    """

    def __init__(self, *args, **kwargs):
        # --- init the parent ---
        super().__init__(*args, **kwargs)
        # --- update the parsable attributes ---
        self._serializable_attributes.extend(['debug'])

        # --- general attributes ---
        self.debug = kwargs.get('debug', False)

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Parameter Creation ----------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def create_parameters(parameters_type: str,
                          arguments: Union[str, dict],
                          parse_instead_of_construct: bool = False,
                          pickled: bool = False):
        """Creates a subclass implementation of the ParametersBase class.

        Args:
            parameters_type: str
                The name of the subclass implementation.
            arguments: Union[str, dict]
                Arguments to use for either construction or parsing of the implementation's information.
            parse_instead_of_construct: bool
                Whether to use the input arguments an inputs to the constructor or parse them as a json object if the
                arguments are a dict.
            pickled: bool
                Whether the arguments are pickled if the input argument is a str.

        Returns:
            ParametersBaseType:
                Subclass of type 'parameters_type'.

        Raises:
            TypeError:
                If the 'arguments' aren't a supported input type.
        """
        if isinstance(arguments, dict):
            if pickled:
                return io.from_pickled_json(arguments)
            if not parse_instead_of_construct:
                return ParametersBase.construct(parameters_type, **arguments)
            else:
                output = ParametersBase.construct(parameters_type)
                output.from_json(arguments)
                return output
        elif isinstance(arguments, str):
            args = io.from_json_str(arguments)
            if pickled:
                return io.from_pickled_json(args)
            if not parse_instead_of_construct:
                return ParametersBase.construct(parameters_type, **args)
            else:
                output = ParametersBase.construct(parameters_type)
                output.from_json(args)
                return output
        else:
            loghandler.log_and_raise(TypeError, "Invalid input arguments type [", type(arguments), "].")

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Manipulation ----------------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    def copy(self, only_if_missing: bool, **kwargs) -> Any:
        """Copies the current Parameters and updates its properties.

        Args:
            only_if_missing: bool
                Indicates whether to only update the properties that are not yet assigned.
            **kwargs:
                The mapping of properties their updated values.

        Returns:
            Any:
                The type of implementation of this ParametersBase class.
        """
        copied_parameters = copy.deepcopy(self)
        copied_parameters.update(only_if_missing, kwargs)
        return copied_parameters

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Debug Properties ------------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    @property
    def has_debug(self) -> bool:
        """Returns whether the debug attribute has been assigned."""
        return self._debug is not None

    @property
    def debug(self) -> bool:
        """Gets whether to perform the related operations in a debug mode.

        Returns:
            bool:
                A boolean representing whether debugging should be performed.

        Raises:
            AttributeError:
                If the property has not been assigned yet.
        """
        if self._debug is None:
            loghandler.log_and_raise(AttributeError, "The debug parameter has not been set.")
        return self._debug

    @debug.setter
    def debug(self, input_value: Optional[bool]):
        """Sets whether to perform the related operations in a debug mode.

        Args:
            input_value: Optional[bool]
                Either None or a bool.

        Raises:
            TypeError:
                If the provided `input_value` is not a supported type.
        """
        if input_value is None or isinstance(input_value, bool):
            self._debug = input_value
        else:
            loghandler.log_and_raise(TypeError, "Invalid input type [", type(input_value), "].")

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Temp Working Directory Handling ---------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    @staticmethod
    def create_temporary_directory(specific_folder_name: str) -> str:
        """Creates a path to a temporary directory without creating the directory on the file system.

        Args:
            specific_folder_name: str
                A sub-folder in the temporary directory parent folder to house the returned unique folder.

        Returns:
            str:
                A unique temporary path in string form.
        """
        return io.get_temp_dir() + "/" + specific_folder_name + "/" + io.get_date_time_string()
