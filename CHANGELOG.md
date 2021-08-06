0.0.8.1 (2021-08-05)
==================
Minor Mistakes:

* [BUG #29](https://github.com/alexhallam/tv/issues/23):
Column count was wrong.
* [BUG #28](https://github.com/alexhallam/tv/issues/19):
Accidental extra info printed from debug.

0.0.9 (2021-08-05)
==================
Feature Enhancement:

* [BUG #23](https://github.com/alexhallam/tv/issues/23):
Simplified the regex for floats.
* [BUG #19](https://github.com/alexhallam/tv/issues/19):
Printing "wide" datasets with more columns than space in the terminal resulted in a poor viewer experience. This fix removes extra columns from the print and mentions them in the footer.
