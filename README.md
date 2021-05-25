[![Rust](https://github.com/alexhallam/tv/actions/workflows/rust.yml/badge.svg)](https://github.com/alexhallam/tv/actions/workflows/rust.yml)

Tidy Viewer (tv) is a csv pretty printer that uses column styling maximize viewer enjoyment.

![Peek 2021-05-25 19-57](https://user-images.githubusercontent.com/9298693/119582922-89857880-bd93-11eb-868a-3d7ff2b9a1a6.gif)

```
old gif
![draft](https://user-images.githubusercontent.com/9298693/117525069-abf35580-af8e-11eb-8384-7e54b02a037e.gif)
```

# Installation

```
git clone https://github.com/alexhallam/tv
cargo build --release
```

# Example


```
# Download the diamonds data
wget https://raw.githubusercontent.com/tidyverse/ggplot2/master/data-raw/diamonds.csv

# pipe 35 records to tv
cat data/diamonds.csv | head -n 35 | tv
```

# Tools to pair with tv

`tv` is a good compliment to command line data manipulation tools. I have listed some tools that I like to use with tv.

`xsv` ([code](https://github.com/BurntSushi/xsv))

`tsv-utils` ([code](https://github.com/eBay/tsv-utils))

`q` ([code](https://github.com/zestyping/q))

`miller` ([code](https://github.com/johnkerl/miller))

# Tools similar to tv

`column` Comes standard with linux.
