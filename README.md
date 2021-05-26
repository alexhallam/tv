[![Rust](https://github.com/alexhallam/tv/actions/workflows/rust.yml/badge.svg)](https://github.com/alexhallam/tv/actions/workflows/rust.yml)

Tidy Viewer (tv) is a csv pretty printer that uses column styling to maximize viewer enjoyment.

![Peek 2021-05-25 20-08](https://user-images.githubusercontent.com/9298693/119583678-1e3ca600-bd95-11eb-80d7-bcbd649e2a07.gif)

# Installation

The current version is alpha. I do not plan to push to crates.io until this is more polished. If you would like to try this in its raw state [install rust](https://www.rust-lang.org/tools/install) and follow the steps below.

1. Clone repo
2. `cargo build --release`
3. cp binary to `bin`

```
git clone https://github.com/alexhallam/tv
cd tv
cargo build --release
sudo cp ./target/release/tv /usr/local/bin/.
```

# Example


```
# Download the diamonds data
wget https://raw.githubusercontent.com/tidyverse/ggplot2/master/data-raw/diamonds.csv

# pipe 35 records to tv
cat diamonds.csv | head -n 35 | tv
```

# Tools to pair with tv

`tv` is a good compliment to command line data manipulation tools. I have listed some tools that I like to use with tv.

`xsv` ([code](https://github.com/BurntSushi/xsv))

`tsv-utils` ([code](https://github.com/eBay/tsv-utils))

`q` ([code](https://github.com/zestyping/q))

`miller` ([code](https://github.com/johnkerl/miller))

# Tools similar to tv

`column` Comes standard with linux.
