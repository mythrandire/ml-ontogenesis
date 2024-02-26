from typing import Optional
import numpy as np
from ml_ontogenesis.utilities import loghandler
from ml_ontogenesis.utilities.parameters_base import ParametersBase


class GenericTorchDatasetParameters(ParametersBase):
    """
    Provides the necessary parameters for generating and loading the Torch Dataset.
    """

    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)

        self._serializable_attributes.extend(['dataset_directory', 'raw_dataset_name'])

        # --- If you have special attributes that you want to define, you can define them thus ---
        # self._specialized_attributes.extend(['alpha_property', 'epsilon'])

        self.dataset_directory = kwargs.get('dataset_directory')
        self.raw_dataset_name = kwargs.get('raw_dataset_name')

        # --- special parameters ---
        # self.alpha_parameter = kwargs.get('alpha_parameter', 'default_value')

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
                If the provided input type is not suppoerted.

        """
        if input_value is None or isinstance(input_value, str):
            self._dataset_directory = input_value
        else:
            loghandler.log_and_raise(TypeError, f"Invalid input type[{type(input_value)}] for dataset_directory.")
