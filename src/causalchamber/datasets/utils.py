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


"""
"""

import numpy as np
import zipfile
import requests
from pathlib import Path
import hashlib
from tqdm import tqdm

# --------------------------------------------------------------------
# Functions to download, extract and verify datasets


def download_and_extract(
    url,
    root,
    checksum=None,
):
    """

    Parameters
    ----------
    url : string
    local_dir : string

    Returns
    -------
    curve_files : list of string
        A list with the paths to all available torque-curve files, to the load e.g. with
        pandas.read_csv.

    """
    local_zipfile = "causal_chamber_" + hashlib.md5(url.encode()).hexdigest() + ".zip"
    zip_path = Path(root, local_zipfile)
    # Download
    _download(url, zip_path)
    # Verify
    if checksum is not None:
        print("  Verifying checksum...", end="")
        md5 = _compute_md5(zip_path, checksum)
        if checksum != md5:
            raise Exception(
                f'Checksum does not match!\n  expected: "{checksum}"\n  computed: "{md5}"'
            )
        else:
            print(" done.")
    # Extract
    print(f'  Extracting zip-file contents to "{root}"...', end="")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(root)
    print(" done.")


def _download(url, output_path):
    print(f'Downloading dataset from "{url}" into "{output_path}"\n')
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)
    with open(output_path, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")


def _unzip(path, output_dir):
    """
    Unzips the file at the given path into the given output_dir.
    """
    print(f'  Extracting "{path}" to "{output_dir}"')
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(output_dir)


def _compute_md5(path, checksum):
    """Verify the MD5 checksum of a file at the given path"""
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        data = f.read()
        hasher.update(data)
    return hasher.hexdigest()


# --------------------------------------------------------------------
# Functions used by experiment protocol generators


def set_and_measure(
    value_ranges,
    n_interventions,
    n_msr,
    repeat=False,
    wait_before_set=0,
    wait_before_msr=0,
    random_state=42,
):
    """Generates a sequence of SET and MSR instructions with optional WAIT
    instructions between them, where the set values, measurement sizes and
    wait times are randomly selected.

    Parameters
    ----------
    value_ranges : dict
        A dictionary where each key is an intervention target to set,
        and each value is a set of possible values it can take.

    n_interventions : int
        The number of intervention cycles
        to perform. Each intervention cycle consists of setting
        values (SET), waiting (WAIT), and measuring (MSR).

    n_msr : int or tuple
        The number of measurements to take in each measurement
        phase. If a tuple, it defines a range of possible numbers to
        randomly sample from.

    repeat : bool, optional
        If True, allows the repetition of the same value for
        subsequent interventions for the same target. If False, each
        intervention for a target must have a different value from the
        last. Default is False.

    wait_before_set : int or tuple, optional
        The waiting time (in milliseconds) before setting values in
        each intervention. If a tuple, it defines a range of possible
        wait times to randomly sample from. Default is 0, meaning no
        WAIT instruction is produced.

    wait_before_msr : int or tuple, optional
        The waiting time (in milliseconds) before measuring after each
        intervention. If a tuple, it defines a range of possible wait
        times to randomly sample from. Default is 0, meaning no WAIT
        instruction is produced.

    random_state : int, optional
        A seed value for the random number generator to ensure
        reproducibility. Default is 42.

    Returns
    -------
    list of str
        A list of strings, each representing an instruction.

    Notes
    -----

    - The function internally uses a random number generator for
      selecting wait times, values to set, and the number of
      measurements.
    - The 'SET' instructions are generated based on the `value_ranges`
      and the `repeat` parameter.
    - The function ensures that each target is set exactly once in
      each intervention cycle.

    """
    # Function implementation
    last_value = dict((target, set()) for target, _ in value_ranges.items())
    instructions = []
    rng = np.random.default_rng(random_state)

    def sample(values):
        if isinstance(values, tuple):
            return rng.integers(values[0], values[1], endpoint=True)
        else:
            return values

    for i in range(n_interventions):
        # WAIT instruction, before measuring
        wait = sample(wait_before_set)
        if wait > 0:
            instructions.append(f"WAIT,{wait}")
        # SET instruction
        for target, values in value_ranges.items():
            possible_values = (
                list(values) if repeat else list(values - last_value[target])
            )
            value = rng.choice(possible_values)
            instructions.append(f"SET,{target},{value}")
            last_value[target] = {value}
        # WAIT instruction, before measuring
        wait = sample(wait_before_msr)
        if wait > 0:
            instructions.append(f"WAIT,{wait}")
        # MSR instruction
        n_measurements = sample(n_msr)
        instructions.append(f"MSR,{n_measurements},0")
    return instructions
