import pytest
import pandas as pd
from ml_ontogenesis.datasets.pytorch_dataset import GenericTorchDataset
from ml_ontogenesis.datasets.pytorch_dataset_parameters import GenericTorchDatasetParameters


@pytest.fixture
def mock_dataset_parameters() -> GenericTorchDatasetParameters:
    parameters = GenericTorchDatasetParameters(version='0.0.1', dataset_directory='/home/mithrandir/')
    return parameters


@pytest.fixture
def torch_dataset_instance(mock_dataset_parameters: GenericTorchDatasetParameters) -> GenericTorchDataset:
    dataset = GenericTorchDataset(raw_dataset=pd.DataFrame({'col1': [1, 2, 3]}))
    dataset.dataset_parameters = mock_dataset_parameters
    return dataset


def test_has_dataset_parameters(torch_dataset_instance: GenericTorchDataset):
    assert torch_dataset_instance.has_dataset_parameters, f"Dataset parameters should be recognized."


def test_dataset_parameters_assignment(torch_dataset_instance: GenericTorchDataset,
                                       mock_dataset_parameters: GenericTorchDatasetParameters):
    assert torch_dataset_instance.dataset_parameters == mock_dataset_parameters, f"Parameters should be assigned."


def test_has_raw_dataset(torch_dataset_instance: GenericTorchDataset):
    assert torch_dataset_instance.has_raw_dataset, f"Raw dataset should be recognized as set."


def test_raw_dataset_assignment(torch_dataset_instance: GenericTorchDataset):
    df = pd.DataFrame({'col1': [1, 2, 3]})
    torch_dataset_instance.raw_dataset = df
    assert torch_dataset_instance.raw_dataset.equals(df), f"Raw dataset should be correctly assigned."


"""
def test_load_raw_dataset(torch_dataset_instance: GenericTorchDataset):
    with pytest.raises(NotImplementedError):
        torch_dataset_instance.load_raw_dataset()


def test_create_raw_dataset(torch_dataset_instance: GenericTorchDataset):
    with pytest.raises(NotImplementedError):
        torch_dataset_instance.create_raw_dataset()


def test_visualize_sample(torch_dataset_instance: GenericTorchDataset):
    with pytest.raises(NotImplementedError):
        torch_dataset_instance.visualize_sample()
"""
