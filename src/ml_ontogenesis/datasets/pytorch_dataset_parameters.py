from typing import Optional
import numpy as np
from ml_ontogenesis.utilities import loghandler
from ml_ontogenesis.utilities.parameters_base import ParametersBase


class GenericTorchDatasetParameters(ParametersBase):
    """
    Provides the necessary parameters for generating and loading the Torch Dataset.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._serializable_attributes.extend(['version', 'dataset_directory'])

        # --- If you have special attributes that you want to define, you can define them thus ---
        # self._specialized_attributes.extend(['alpha_property', 'epsilon'])
        self.version = kwargs.get('version')
        self.dataset_directory = kwargs.get('dataset_directory')

        # --- special parameters ---
        # self.alpha_parameter = kwargs.get('alpha_parameter', 'default_value')

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Parsable methods ------------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #

    @property
    def has_version(self) -> bool:
        """Returns whether the version has been assigned."""
        return self._version is not None

    @property
    def version(self) -> str:
        """
        Gets the version of this implementation of the Parsable class.

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
        if self._version is None:
            loghandler.log_and_raise(AttributeError, "The dataset version has not been set.")
        return self._version

    @version.setter
    def version(self, input_value: Optional[str]):
        """
        Sets the version of this implementation of the Parsable class.

        Args:
            input_value: Optional[str]
                None or a string representation of the version.

        Raises:
            TypeError:
                If the provided `input_value` is not a supported type.
        """
        if input_value is None or isinstance(input_value, str):
            self._version = input_value
        else:
            loghandler.log_and_raise(TypeError, f"Invalid input type [{type(input_value)}] for dataset version.")

    @property
    def has_dataset_directory(self) -> bool:
        """Returns whether the directory of the dataset has been assigned."""
        return self._dataset_directory is not None

    @property
    def dataset_directory(self) -> str:
        """Gets the directory where the dataset is stored.

        Returns:
            str:
                The file path to the directory
        Raises:
            AttributeError:
                If the property has not been assigned.

        """
        if self._dataset_directory is None:
            loghandler.log_and_raise(AttributeError, "The dataset directory has not been set.")
        return self._dataset_directory

    @dataset_directory.setter
    def dataset_directory(self, input_value: Optional[str]):
        """Sets the dataset directory.

        Args:
            input_value: Optional[str]
                Either none or a string
        Raises:
            TypeError:
                If the provided input type is not supported.

        """
        if input_value is None or isinstance(input_value, str):
            self._dataset_directory = input_value
        else:
            loghandler.log_and_raise(TypeError, f"Invalid input type[{type(input_value)}] for dataset_directory.")
