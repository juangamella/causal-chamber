# Examples used in src/README.md

# ----------------------------------------------------------------------

import causalchamber.datasets as datasets

# Download the dataset and store it, e.g., in the current directory
dataset = datasets.Dataset(name="lt_camera_test_v1", root="./", download=True)

# Select an experiment and load the observations and images
experiment = dataset.get_experiment(name="palette")
observations = experiment.as_pandas_dataframe()
images = experiment.as_image_array(size="200")

# ----------------------------------------------------------------------

datasets.list_available()

# Output:
# Available datasets (last changes on 2024-03-26):
#
#   lt_camera_walks_v1
#   lt_test_v1
#   wt_intake_impulse_v1
#   lt_malus_v1
#   lt_camera_test_v1
#   wt_test_v1
#
# Visit https://causalchamber.org for a detailed description of each dataset.

# ----------------------------------------------------------------------

output = dataset.available_experiments()

print(output)
# Output:
# ['palette',
#  'polarizer_effect_bright',
#  'polarizer_effect_dark',
#  'pure_colors_bright',
#  'pure_colors_dark']

# ----------------------------------------------------------------------

output = experiment.available_sizes()
print(output)
# Output:
# ['200', '500', 'full']

# ----------------------------------------------------------------------
import numpy as np
from causalchamber.models import model_a1

output = model_a1(L=np.linspace(0, 1, 10), L_min=0.1, omega_max=314.15)

print(output)

# Output:

# array([ 31.415     ,  34.90555556,  69.81111111, 104.71666667,
#        139.62222222, 174.52777778, 209.43333333, 244.33888889,
#        279.24444444, 314.15      ])
