# Rudimentary Type Detection

This directory contains the rudimentary type detection engine used for CSV 
dialect detection. It is a regular-expression based method that allows 
detection of:

- Empty cells
- URLs and email
- Numbers, including scientific notation, comma/period as radix point, 
  comma/period as thousands separator.
- Percentages
- Currencies
- Time in HH:MM:SS, HH:MM, and H:MM notation
- Dates in forty different formats, including Chinese. Based on [this 
  Wikipedia article](https://en.wikipedia.org/wiki/Date_format_by_country).
- Combined date and time (i.e. ISO 8601 and variations)
- N/A and n/a

This covers about 80% - 90% of cells in our collection of CSV files.

Copyright (c) 2018 The Alan Turing Institute

## Author

Gerrit J.J. van den Burg, gvandenburg@turing.ac.uk
