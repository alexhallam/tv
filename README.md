[![Rust](https://github.com/alexhallam/tv/actions/workflows/rust.yml/badge.svg)](https://github.com/alexhallam/tv/actions/workflows/rust.yml)
[![Crate](https://img.shields.io/crates/v/tidy-viewer.svg)](https://crates.io/crates/tidy-viewer)

<h1 align="center">Tidy Viewer (tv)</h1>
<p align="center">Tidy Viewer (tv) is a cross-platform csv pretty printer that uses column styling to maximize viewer enjoyment.</p>

![logo](img/TVBlue.png)

# Pretty Printing

![example](img/starwars.png)


# Installation

The following install options are available

1. Cargo Install from crates.io
2. Debian `.deb` install
3. AUR
4. MacOS
5. ARM
6. Windows
7. Build from source (Most general)
8. Snap

### 1. Cargo Install

The following will install from the [crates.io](https://crates.io/crates/tidy-viewer) source. For convenience add the alas `alias tv='tidy-viewer'` to bashrc.

```sh
cargo install tidy-viewer
sudo cp /home/$USER/.cargo/bin/tidy-viewer /usr/local/bin/.
echo "alias tv='tidy-viewer'" >> ~/.bashrc
source ~/.bashrc
```

### 2. Debian

```sh
wget tidy-viewer_<VERSION>_amd64.deb
sudo dpkg -i target/debian/tidy-viewer_<VERSION>_amd64.deb
echo "alias tv='tidy-viewer'" >> ~/.bashrc
source ~/.bashrc
```

### 3. AUR

Kindly maintained by @yigitsever

```sh
paru -S tidy-viewer
```

### 4-7. Other releases

We currently cut releases for the following architectures. Download from the [release page](https://github.com/alexhallam/tv/releases).

* **MacOS**
* **ARM**
* **Windows**
* **Build from source (Most general)**

The instuctions for all of the above are very similar with the following general steps.

1. Download your desired release from the [release page](https://github.com/alexhallam/tv/releases)
2. `tar -xvzf <RELEASE_FILE_NAME>`
3. `cd` into uncompressed folder
4. Find binary `tidy-viewer`

After the above steps I would highly reccomend you make an alias for `tidy-viewer` as shown for other builds.

### 8. Snap

```
sudo snap install --edge tidy-viewer
tidy-viewer --help
```

# Examples

Have some fun with the following datasets!

### Diamonds
```sh
# Download the diamonds data
wget https://raw.githubusercontent.com/tidyverse/ggplot2/master/data-raw/diamonds.csv

# pipe to tv
cat diamonds.csv | tv
```

### Starwars
```sh
wget https://raw.githubusercontent.com/tidyverse/dplyr/master/data-raw/starwars.csv

# Pass as agrument
tv starwars.csv
```

### Pigeon Racing
```sh
wget https://raw.githubusercontent.com/joanby/python-ml-course/master/datasets/pigeon-race/pigeon-racing.csv
cat pigeon-racing.csv | tv
```

# Significant Figure Definitions & Rules

![example](img/sigs.png)

![example](img/long_double.png)

> The first three digits represent > 99.9% the value of a number. -- GNU-R Pillar

`tv` uses the same significant figure (sigfig) rules that the R package `pillar` uses.

The purpose of the sigfig rules in `tv` is to guide the eye to the most important information in a number. This section defines terms and the decision tree used in the calculation of the final value displayed.

## Definitions

```text
     ┌─────┐      ┌─────┐     ─┐
     │     │      │     │      │
     │     │      │     │      │
     │     │      │     │      │
     │     │      │     │      │
     │     │  ┌┐  │     │      │
     └─────┘  └┘  └─────┘    ──┴─
   │        │    │                │
   └────────┘  ▲ └────────────────┘
left hand side │  right hand side
     (lhs)     │       (rhs)

            decimal
```

**left hand side (lhs)**: digits on the left hand side of the decimal.

**right hand side (rhs)**: digits on the right hand side of the decimal.

```text

 ┌─────┐      ┌─────┐     ─┐     ┌─────┐
 │     │      │     │      │     │     │
 │     │      │     │      │     │     │
 │     │      │     │      │     │     │
 │     │      │     │      │     │     │
 │     │  ┌┐  │     │      │     │     │
 └─────┘  └┘  └─────┘    ──┴─    └─────┘

│                     │         │       │
└─────────────────────┘         └───────┘
       leading 0s              trailing 0s
```
**leading 0s**: 0s to the left of a non-zero.

**trailing 0s**: 0s to the right of a non-zero. The zeros in 500m are trailing as well as the 0s in 0.500km. 


```text
 ─┐     ┌─────┐       ─┐
  │     │     │        │
  │     │     │        │
  │     │     │        │
  │     │     │        │
  │     │     │  ┌┐    │
──┴─    └─────┘  └┘  ──┴─

                   │        │
                   └────────┘
              fractional digit(s)
```

**fractional digits**: Digits on the rhs of the decimal. The represent the non-integer part of a number.

## Rules

There are only 4 outputs possible. The significant figures to display are set by the user. Assume `sigfig = 3`:

1. **lhs only (`12345.0 -> 12345`)**: If no fractional digits are present and lhs >= sigfig then return lhs
2. **lhs + point (`1234.5 -> 1234.`)**: If fractional digits are present and lhs >= sigfig then return lhs with point. This is to let the user know that some decimal dust is beyond the main mass of the number.
3. **lhs + point + rhs (`1.2345 -> 1.23`)**: If fractional digits are present and lhs < sigfig return the first three digits of the number.
4. **long rhs (`0.00001 -> 0.00001`)**: This is reserved for values with leading 0s in the rhs.



```text
# Psuedo Code: Sigfig logic assuming sigfig = 3
if lhs == 0:
    n = ((floor(log10(abs(x))) + 1 - sigfig)
    r =(10^n) * round(x / (10^n))
    return r
    // (0.12345 -> 0.123)
else:
    if log10(lhs) + 1 > sigfig:
        if rhs > 0:
            //concatenate:
            //(lhs)
            //(point)
            //(123.45 -> 123.)
        else:
            //concatenate:
            //(lhs)
            //(1234.0 -> 1234)
            //(100.0 -> 100)
    else:
        //concatenate:
        //(lhs)
        //(point)
        //sigfig - log10(lhs) from rhs
        //(12.345 -> 12.3)
        //(1.2345 -> 1.23)
```

# Tools to pair with tv

`tv` is a good compliment to command line data manipulation tools. I have listed some tools that I like to use with tv.

[xsv](https://github.com/BurntSushi/xsv) - Command line csv data manipulation. [Rust | CLI]

[csvtk](https://bioinf.shenwei.me/csvtk/) - Command line csv data manipulation. [Go | CLI]

[tsv-utils](https://github.com/eBay/tsv-utils) - Command line csv data manipulation toolkit. [D | CLI]

[q](https://github.com/zestyping/q) - Command line csv data manipulation query-like. [Python | CLI]

[miller](https://github.com/johnkerl/miller) - Command line data manipulation, statistics, and more. [C | CLI]

[VisiData](https://www.visidata.org/) - An interactive terminal user interface that is built to explore and wrangle data. [Python | TUI]

# Tools similar to tv

`column` Comes standard with linux. To get similar functionality run `column file.csv -ts,`

Though `column` is similar I do think there are some reasons `tv` is a better tool.

## 1. NA comprehension

`NA` values are very important! Viewers should have their attention drawn to these empty cells. In the image below `NA` values are not only invisible, but it seems to be causing incorrect alignment in other columns.

![na_comp](img/pigeon-racing.png)

## 2. Column Overflow Logic

In cases where the terminal width can't fit all of the columns in a dataframe, column will try to smush data on the rows below. This results in an unpleasant viewing experience. 

`tv` can automatically tell when there will be too many columns to print. When this occurs it will only print the columns that fit in the terminal and mention the extras in the footer below the table.

![overflow](img/pigeon-racing.png)

# Help

`tv --help`

```txt
tv 0.0.20
Tidy Viewer (tv) is a csv pretty printer that uses column styling to maximize viewer enjoyment.✨✨📺✨✨

    Example Usage:
    wget https://raw.githubusercontent.com/tidyverse/ggplot2/master/data-raw/diamonds.csv
    cat diamonds.csv | head -n 35 | tv

USAGE:
    tv [FLAGS] [OPTIONS] [FILE]

FLAGS:
    -d, --debug-mode    Print object details to make it easier for the maintainer to find and resolve bugs.
    -h, --help          Prints help information
    -V, --version       Prints version information

OPTIONS:
    -c, --color <color>
            There are 4 colors (1)nord, (2)one_dark, (3)gruvbox, and (4)dracula. An input of (0)bw will remove color
            properties. Note that colors will make it difficult to pipe output to other utilities [default: 1]
    -s, --delimiter <delimiter>                      The delimiter separating the columns. [default: ,]
    -f, --footer <footer>                            Add a title to your tv. Example 'footer info' [default: NA]
    -l, --lower-column-width <lower-column-width>
            The lower (minimum) width of columns. Must be 2 or larger. [default: 2]

    -n, --number of rows to output <row-display>     Show how many rows to display. [default: 25]
    -t, --title <title>                              Add a title to your tv. Example 'Test Data' [default: NA]
    -u, --upper-column-width <upper-column-width>    The upper (maxiumum) width of columns. [default: 20]

ARGS:
    <FILE>    File to process
```
# Inspiration

[pillar](https://pillar.r-lib.org/dev/articles/digits.html#trailing-dot-1) - R's tibble like formatting. Fantastic original work by [Kirill Müller](https://github.com/krlmlr) and [Hadley Wickham](http://hadley.nz/). `tv` makes an attempt to port their ideas to the terminal.
