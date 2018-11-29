# Design document for storing results

A result is stored in [JSON Lines format](http://jsonlines.org/) with the 
following fields:

- filename: filename of the CSV file, typically ``/path/to/data/[md5hash].csv``

- status: parsing status, either ``null``, ``ok``, ``fail``, or ``skip``.

- reason: failure or skip reason, either ``null`` or:

   + ``unknown``,
   + ``multiple_answers``,
   + ``no_results``,
   + ``timeout``,
   + ``unreadable``
   + ``non_existent``

- detector: name of the detector

- hostname: hostname of the pc that ran the detection

- runtime: time it took to run the detection

- dialect. See below.

A dialect is a separate key/value map using the fields:

- delimiter: single character string, empty string for single-column files, 
  ``null`` for undefined.

- quotechar: single character string, empty string for unquoted files, 
  ``null`` for undefined.

- escapechar: single character string, empty string for no escape char, 
  ``null`` for undefined
