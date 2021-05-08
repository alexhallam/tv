[![Rust](https://github.com/alexhallam/tv/actions/workflows/rust.yml/badge.svg)](https://github.com/alexhallam/tv/actions/workflows/rust.yml)

Tidy Viewer (tv) is a csv pretty printer that uses column styling maximize viewer enjoyment.

![draft](https://user-images.githubusercontent.com/9298693/117525069-abf35580-af8e-11eb-8384-7e54b02a037e.gif)

# Installation

```
git clone https://github.com/alexhallam/tv
cargo build --release
```

# Usage

```
cat a.csv | tv
```

# Tools to pair with tv

`tv` is a good compliment to command line data manipulation tools. 

`xsv` ([code](https://github.com/BurntSushi/xsv))

`tsv-utils` ([code](https://github.com/eBay/tsv-utils))

`q` ([code](https://github.com/zestyping/q))

`miller` ([code](https://github.com/johnkerl/miller))
