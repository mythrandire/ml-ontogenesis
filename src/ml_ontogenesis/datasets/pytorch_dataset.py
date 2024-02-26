import abc
import torch
from torch.utils.data import Dataset
from typing import Optional
import pandas as pd

from ml_ontogenesis.utilities import GenericParsable, loghandler
from ml_ontogenesis.datasets.pytorch_dataset_parameters import GenericTorchDatasetParameters


class GenericTorchDataset(GenericParsable, Dataset):
    """
    A generic dataset class that inherits from GenericParsable and torch.utils.data.Dataset
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raw_dataset = kwargs.get("raw_dataset")

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Dataset Parameters ----------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #

    @property
    def has_dataset_parameters(self) -> bool:
        """Returns whether the dataset parameters have been assigned."""
        return self._dataset_parameters is not None

    @property
    def dataset_parameters(self) -> GenericTorchDatasetParameters:
        """Gets the GenericTorchDatasetParameters used to control the processing of datasets.

        Returns:
            GenericTorchDatasetParameters:
                A valid instance of the GenericTorchDatasetParameters class.
        Raises:
            AttributeError:
                If the property has not been assigned.

        """
        if self._dataset_parameters is None:
            loghandler.log_and_raise(AttributeError, "The dataset parameters have not been set.")
        return self._dataset_parameters

    @dataset_parameters.setter
    def dataset_parameters(self, input_value: Optional[GenericTorchDatasetParameters]):
        """Sets the GenericTorchDatasetParameters used to control the processing of datasets.

        Args:
            input_value: Optional[GenericTorchDatasetParameters]
                         Either None or valid instance of GenericTorchDatasetParameters
        Raises:
            TypeError:
                If the provided input type is not supported.

        """
        if input_value is None or isinstance(input_value, GenericTorchDatasetParameters):
            self._dataset_parameters = input_value
        else:
            loghandler.log_and_raise(TypeError, f"Invalid input type [{type(input_value)}] for GenericTorchDatasetParameters.")

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Raw Dataset Properties ------------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #
    @property
    def has_raw_dataset(self) -> bool:
        """Returns whether the raw dataset has been assigned."""
        return self._raw_dataset is not None

    @property
    def raw_dataset(self) -> pd.DataFrame:
        """Gets the raw dataset.

        Returns:
            pandas.DataFrame:
                A valid pandas.DataFrame

        Raises:
            AttributeError:
                If the property has not been assigned successfully.

        """
        if self._raw_dataset is None:
            loghandler.log_and_raise(AttributeError, "The raw dataset has not been set.")
        return self._raw_dataset

    @raw_dataset.setter
    @GenericTorchDatasetParameters.static_class_setter()
    def raw_dataset(self, input_value: Optional[pd.DataFrame]):
        """Sets the raw dataset.

        Args:
            input_value: Optional[pandas.DataFrame]
                Either None or a pandas.DataFrame

        Raises:
            TypeError:
                If the provided input type is not supported.

        """
        if input_value is None or isinstance(input_value, pd.DataFrame):
            self._raw_dataset = input_value
        else:
            loghandler.log_and_raise(TypeError, f"Invalid input type [{type(input_value)}] for raw dataset.")

    # @abc.abstractmethod
    # def load_raw_dataset(self):
    #     """Loads the raw dataset from the filename in the parameters."""
    #     pass  # pragma: no cover

    # ---------------------------------------------------------------------------------------------------------------- #
    # --- Dataset Creation Methods ----------------------------------------------------------------------------------- #
    # ---------------------------------------------------------------------------------------------------------------- #

    # @abc.abstractmethod
    # def create_raw_dataset(self, *args, **kwargs):
    #    """Populates the raw dataset from the relevant parameters in the GenericTorchDatasetParameters."""
    #     pass  # pragma: no cover

    # @abc.abstractmethod
    # def visualize_sample(self, *args, **kwargs):
    #     """Method to visualize individual samples/rows in the dataset"""
    #     pass  # pragma: no cover
