# gom

`gom` is a CLI tool that displays a human-readable table with GPU usage information. Think `nvidia-smi`, but minimalist and pretty.

It also shows per-container GPU usage information if Docker is installed.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `gom`.

## Usage

`gom show` displays a table with GPU usage information.

`gom watch` displays a table with GPU usage information and updates it every second.

## Screenshots

Compare the output of `gom show` and `nvidia-smi`. I hope you'll agree that `gom` produces more clear and helpful output (ex. it breaks usage down across the 4 running Docker containers), while `nvidia-smi` is long and complex (I couldn't even screenshot the whole thing).

![gom show image](https://github.com/nebrelbug/gom/assets/25597854/367004c2-8729-491d-bff4-783a145fa7bb)

![nvidia-smi image](https://github.com/nebrelbug/gom/assets/25597854/80380be6-b7d2-43c0-b10c-07267b85613e)

## Troubleshooting

You may need to install a different version of `pynvml` depending on your CUDA version.
