# MIT License

# Copyright (c) 2024 Juan L. Gamella

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import causalchamber.datasets.utils as utils
from pathlib import Path
import pandas as pd
import yaml
from PIL import Image
import numpy as np
import os
import requests

"""
This module defines the functions to download datasets and load them as pandas dataframes or numpy arrays.
"""

# --------------------------------------------------------------------
# Download the list of available datasets when this module is imported
DIRECTORY_URL = (
    "https://causalchamber.s3.eu-central-1.amazonaws.com/downloadables/directory.yaml"
)

print(f"\nFetching list of available datasets from {DIRECTORY_URL} ...", end="")

r = requests.get(DIRECTORY_URL)
if r.status_code != 200:
    raise ConnectionError(f'Unexpected HTTP status code "{r.status_code}: {r}".')
directory = yaml.load(r.content, Loader=yaml.Loader)
print(" done.")


def list_available():
    available_datasets = directory["datasets"].keys()
    print(f"Available datasets (last changes on {directory['last_updated']}):\n")
    for d in available_datasets:
        print(f"  {d}")
    print(
        "\nVisit https://causalchamber.org for a detailed description of each dataset."
    )
    return list(available_datasets)


# --------------------------------------------------------------------
# Base Dataset and Experiment classes


class Dataset:
    def __init__(self, name, root, download=True):
        available_datasets = directory["datasets"].keys()
        if name not in available_datasets:
            string = ""
            for d in available_datasets:
                string += '  "' + d + '"\n'
            raise ValueError(
                f'Dataset "{name}" is not available. Available datasets:\n{string}'
            )
        # Store attributes
        self.name = name
        self.root = root
        self.image = directory["datasets"][name]["image"]
        self.chamber = directory["datasets"][name]["chamber"]
        # Check if dataset has already been downloaded to root
        dataset_dir = Path(self.root, self.name)
        if os.path.isdir(dataset_dir):
            print(f'Dataset {self.name} found in "{dataset_dir}".')
        else:
            if download:
                # Download, verify and extract
                self.url = directory["datasets"][name]["url"]
                self.checksum = directory["datasets"][name]["md5"]
                utils.download_and_extract(self.url, self.root, self.checksum)
            else:
                raise FileNotFoundError(
                    f'Could not find dataset directory "{dataset_dir}". Set download=True or choose another root directory (root).'
                )
        # Load available experiments
        #   If not an image dataset, experiments are just .csv files in the dataset directory
        #   If an image dataset, each experiment is a folder
        #   containing the .csv file with measurements and a subfolder
        #   with the images

        if self.image:
            experiment_names = [p.name for p in Path(self.root).glob(f"{self.name}/*")]
            csv_paths = [
                Path(self.root, self.name, e, f"{e}.csv") for e in experiment_names
            ]
            experiments = [ImageExperiment(self.name, path) for path in csv_paths]
        else:
            csv_paths = [p for p in Path(self.root).glob(f"{self.name}/*.csv")]
            experiments = [Experiment(self.name, path) for path in csv_paths]
        # Store experiment dictionary
        assert len(experiments) > 0
        self.__experiments = dict((e.name, e) for e in experiments)

    def available_experiments(self):
        """Return the list of available experiments in this dataset."""
        return list(self.__experiments.keys())

    def get_experiment(self, name):
        """Return a particular experiment given its name (see Experiment or ImageExperiment classes)."""
        return self.__experiments[name]


class Experiment:
    def __init__(self, dataset_name, csv_path):
        self.dataset = dataset_name
        self.csv_path = csv_path
        self.name = csv_path.stem
        self.columns = pd.read_csv(self.csv_path, nrows=0).columns.tolist()

    def as_pandas_dataframe(self):
        """Returns a pandas dataframe with the experiment data (excl. images)"""
        return pd.read_csv(self.csv_path)

    def as_image_array(self):
        raise NotImplementedError("This is not an image dataset!")


class ImageExperiment(Experiment):
    def __init__(self, dataset_name, csv_path):
        super().__init__(dataset_name, csv_path)
        self.image_folders = {}
        for path in [p for p in Path(csv_path.parents[0]).glob("images_*")]:
            size = path.stem.split("_")[1]
            self.image_folders[size] = path

    def available_sizes(self):
        """Returns the available image sizes. Size is given in pixels, where `full` means `2000x2000 px'."""
        return list(self.image_folders.keys())

    def as_image_array(self, size):
        """Returns a numpy array with all the images along the first dimension (axis-0)"""
        if size not in self.image_folders.keys():
            raise ValueError(
                f" Size {size} not available; available image sizes: {list(self.image_folders.keys())}."
            )
        image_filenames = pd.read_csv(self.csv_path).image_file
        image_folder = self.image_folders[size]
        image_paths = [Path(image_folder, f) for f in image_filenames]
        return np.array([np.array(Image.open(f)) for f in image_paths])
