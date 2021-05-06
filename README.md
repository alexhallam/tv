Current functions will read vectors and have logic to convert missing values to NA and align decimals. 

# Goals
1. Pretty print csv and allow users to make their own themes and have access to as many data elements as possible so themes can be flexible
2. Infer schemas from csv to allow users to style by column type or to define their own column type

![draft](https://user-images.githubusercontent.com/9298693/117234109-5b46f580-adf2-11eb-86ac-20c7d7e9ff26.gif)


# Todo

1. It sounds funny, but I can't figure out how to print the columns next to eachother. 
2. I would eventuall like to color NAs.
3. I would like to infer the data types of the columns. Users would have the choice of styling data types in different ways.
4. In the end I would like to as complete as possible, I am trying to stay close to the features found in https://pillar.r-lib.org/ and https://tibble.tidyverse.org/. I figure the teams that made those libraries put a lot of thought into their work and maybe I can just build on their ideas.

# Package structure questions
1. I am not sure if this should be a library, cli, or both
2. I am having difficulty thinking about what Structs should exist. Cells, Columns (Pillars), Table (many columns)? 
3. (probably out of scope, but something I would eventually like to make) Should this be integrated with a TUI allowing a user to select a column and fuzzy-find filter or is this functionality out of scope for a package focused on columns styles?

```
original chars: ["abc", "abcde", "abcdefgh", "abcdefghijkl", "", "", "abcdefghijklmnop"]
original doubles: ["0.0001", "0.001", "0.01", "0.1", "1", "", "100"]
<pillar>
<char>
  0.0001
  0.001
  0.01
  0.1
  1
NA
100
100
<pillar>
<char>
abc
abcde
abcdef…
abcdef…
NA
NA
abcdef…
abcdef…
```
