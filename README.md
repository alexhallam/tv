[![Rust](https://github.com/alexhallam/tv/actions/workflows/rust.yml/badge.svg)](https://github.com/alexhallam/tv/actions/workflows/rust.yml)

Tidy Viewer (tv) is a csv pretty printer that uses column styling maximize viewer enjoyment.


https://user-images.githubusercontent.com/9298693/119566134-cbed8c00-bd78-11eb-9879-8b32b8cbec77.mp4


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
