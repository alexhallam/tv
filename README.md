[![Rust](https://github.com/alexhallam/tv/actions/workflows/rust.yml/badge.svg)](https://github.com/alexhallam/tv/actions/workflows/rust.yml)

<h1 align="center">Tidy Viewer (tv)</h1>
<p align="center">Tidy Viewer (tv) is a csv pretty printer that uses column styling to maximize viewer enjoyment.</p>



![tv](https://user-images.githubusercontent.com/9298693/119914414-064c5a00-bf2e-11eb-8daf-017e1289369a.gif)

# Installation

### 1. Cargo Install

The following will install from the [crates.io](https://crates.io/crates/tidy-viewer) source.

```
cargo install tidy-viewer
sudo cp /home/ubuntu/.cargo/bin/tidy-viewer /usr/local/bin/.
```

For convenience add the alas `alias tv='tidy-viewer'` to bashrc.

```
echo `alias tv='tidy-viewer'` >> `~/.bashrc`
```

### 2. Install from source

The current version is alpha. I do not plan to push to crates.io until this is more polished. If you would like to try this in its raw state [install rust](https://www.rust-lang.org/tools/install) and follow the steps below.

1. Clone repo
2. `cargo build --release`
3. cp binary to `bin`
4. Add `alias tv='tidy-viewer'` to `~/.bashrc`

```
git clone https://github.com/alexhallam/tv
cd tv
cargo build --release
sudo cp ./target/release/tv /usr/local/bin/.
echo `alias tv='tidy-viewer'` >> `~/.bashrc`
```

# Example


```
# Download the diamonds data
wget https://raw.githubusercontent.com/tidyverse/ggplot2/master/data-raw/diamonds.csv

# pipe 35 records to tv
cat diamonds.csv | head -n 35 | tv
```

# Rules (In-progress)

I would like to get some sig-fig logic in here.

## Float

Print only the first three digits. The first three digits represent > 99.9% the value of a number.


# Tools to pair with tv

`tv` is a good compliment to command line data manipulation tools. I have listed some tools that I like to use with tv.

[xsv](https://github.com/BurntSushi/xsv) - Command line csv data manipulation. Rust

[csvtk](https://bioinf.shenwei.me/csvtk/) - Command line csv data manipulation. Go

[tsv-utils](https://github.com/eBay/tsv-utils) - Command line csv data manipulation toolkit. D

[q](https://github.com/zestyping/q) - Command line csv data manipulation query-like. Python

[miller](https://github.com/johnkerl/miller) - Commane line data manipulaiton, statistics, and more. C

[xsv](https://github.com/BurntSushi/xsv) - a command line program for indexing, slicing, analyzing, splitting and joining CSV files

[tsv-utils](https://github.com/eBay/tsv-utils) - command line utilities for tabular data files

[q](https://github.com/zestyping/q) - q is a command line tool that allows direct execution of SQL-like queries on CSVs/TSVs 

[miller](https://github.com/johnkerl/miller) - Miller is like awk, sed, cut, join, and sort for data formats such as CSV, TSV, tabular JSON and positionally-indexed.

# Tools similar to tv

`column` Comes standard with linux.

# Inspiration

[pillar](https://pillar.r-lib.org/dev/articles/digits.html#trailing-dot-1) - R's tibble like formatting

