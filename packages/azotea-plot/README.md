# AZOPLOT

`azoplot` is a command-line plotting utility for debayerized RAW astronomical images. It displays the four Bayer channels of a selected image together with pixel statistics computed in a user-defined Region of Interest (ROI).

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Options](#options)
- [Examples](#examples)

## Installation

Install `azotea-plot` in the same activated virtual environment where `azotea-cli` is installed:

```bash
pip install azotea-plot
```

After installation, check the available commands and options with:

```bash
azoplot --help
```

## Usage

The current command is `stats`. It plots a single RAW image and shows statistics for the selected ROI.

```bash
azoplot stats --image-file <path-to-image> [options]
```

By default, `azoplot` uses a 500 × 400 pixel ROI and automatically scales the displayed pixel values using one standard deviation around the image statistics.

## Options

### Input selection

One of the following options is required:

| Option | Description |
|---|---|
| `-f, --image-file <path>` | Path to a single RAW/FITS image file. |
| `-d, --images-dir <path>` | Path to a directory containing images. |

> **Note:** Directory-based visualization is not implemented yet.

### ROI selection

| Option | Description | Default |
|---|---|---|
| `--x1 <pixels>` | X coordinate of the ROI origin. | Automatically centered |
| `--y1 <pixels>` | Y coordinate of the ROI origin. | Automatically centered |
| `-x, --width <pixels>` | ROI width in pixels. | `500` |
| `-y, --height <pixels>` | ROI height in pixels. | `400` |

### Display scaling

| Option | Description | Default |
|---|---|---|
| `--vmin <value>` | Minimum pixel value to display. | Automatic |
| `--vmax <value>` | Maximum pixel value to display. | Automatic |
| `--sigmas-min <1-5>` | Lower display limit, in standard deviations below the mean. | `1` |
| `--sigmas-max <1-5>` | Upper display limit, in standard deviations above the mean. | `1` |

If `--vmin` and `--vmax` are provided, they take precedence over the automatic sigma-based scaling.

## Examples

Plot an image using the default centered ROI and automatic display scaling:

```bash
azoplot --console --log-level info --trace stats \
    --image-file images/Carpeta1/2020_12_1200_02_329999.CR2 \
    --width 500 \
    --height 400
```

Plot an image with an explicit ROI and fixed display limits:

```bash
azoplot --console --log-level info --trace stats \
    --image-file images/Carpeta1/2020_12_1200_02_329999.CR2 \
    --x1 60 \
    --y1 50 \
    --width 500 \
    --height 400 \
    --vmin 900 \
    --vmax 1100
```

## Help

For the complete and current list of global and command-specific options:

```bash
azoplot --help
azoplot stats --help
```
