List of all municipalities in the state of New Jersey (USA), including GeonamesID.

## Data

Data comes from multiple sources as follows:

List of municipality names, populations, type and form of government in `nj-municipalities-wikipedia` are from [Wikipedia](http://en.wikipedia.org/wiki/List_of_municipalities_in_New_Jersey).

GeonamesID for each municipality is extracted from an API query to [geonames.org](http://http://www.geonames.org).

## Preparation

This package includes a Python script to fetch the GeonamesIDs for each municipality and output a combined JSON of all the municipality information.  A handful of entries were hand-extracted when the automated search failed.

Install the requirements:

    pip install -r scripts/requirements.pip

Edit `scripts/settings.cfg` and put in your Geonames API username.

Run the python script to generate the json file:

    python scripts/fetch-geonames-ids.py

## License

Copyright (c) 2015 Rahul Bhargava

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.