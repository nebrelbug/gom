# gom

`gom` displays a human-readable table with GPU usage information. Think `nvidia-smi`, but minimalist and pretty. 

It also shows per-container GPU usage information if Docker is installed.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `gom`.

## Usage

`gom show` displays a table with GPU usage information.

`gom watch` displays a table with GPU usage information and updates it every second.

## Troubleshooting

You may need to install a different version of `pynvml` depending on your CUDA version. 