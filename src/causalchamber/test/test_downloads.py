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

import unittest

import pandas as pd

col_numbers = {
    "lt": {"standard": 46, "camera": 52},
    "wt": {
        "standard": 37,
        "pressure-control": 45,
    },
}


class DownloadTests(unittest.TestCase):
    def test_workflow(self):
        """Test that all datasets listed in the directory are downloadable and
        their experiments accessible. Check that the number of columns is
        consistent across experiments and with the corresponding chamber
        configuration."""
        import causalchamber.datasets

        available = causalchamber.datasets.list_available()
        for name in available:
            print(f"dataset: {name}")
            dataset = causalchamber.datasets.Dataset(
                name=name, root="/tmp", download=True
            )
            experiments = dataset.available_experiments()
            print(experiments)
            prev_columns = None
            prev_config = None
            for e in experiments:
                experiment = dataset.get_experiment(e)
                df = experiment.as_pandas_dataframe()
                print(f"  experiment: {e}")
                print(f"    {len(df)} observattions")
                print(f"    columns {len(df.columns)}")
                # Check column names and chamber config are consistent across the experiments of this dataset.
                if prev_columns is None:
                    for c in df.columns:
                        print("     ", c)
                    prev_columns = df.columns
                    config = pd.unique(df.config)
                    self.assertEqual(len(config), 1)
                    prev_config = config[0]
                    self.assertEqual(
                        len(df.columns), col_numbers[dataset.chamber][config[0]]
                    )
                else:
                    self.assertTrue((df.columns == prev_columns).all())
                    config = pd.unique(df.config)
                    self.assertEqual(len(config), 1)
                    self.assertEqual(config[0], prev_config)
                    self.assertEqual(
                        len(df.columns), col_numbers[dataset.chamber][config[0]]
                    )
                # If an image dataset, check that all available sizes can be loaded
                if dataset.image:
                    sizes = experiment.available_sizes()
                    print(f"    available image sizes: {sorted(sizes)}")
                    for size in sorted(sizes):
                        print(f"      loading size {size}")
                        images = experiment.as_image_array(sorted(sizes)[0])
                        self.assertEqual(len(df), len(images))
                        print("      ok.")
