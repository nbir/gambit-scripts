# Gambit - Research scripts [gangActivityAnalysis]


Research scripts for [Gambit](http://brain.isi.edu/~gambit/v2.0/)
| [CBG](http://cbg.isi.edu) ISI, University of Southern California, Los Angeles, CA

## Contributors

* [Nibir Bora](http://nibir.me/) | <nbora@usc.edu>
* [Vladimir Zaytsev](http://zvm.me/) | <zaytsev@usc.edu>


## Input files
 #TODO

## Run directives

Format: `python run.py -<option> <parameters>`

Prepare data:

* `-get all` - Get all tweets inside bounds
* `-prep trim-ngang` - Trim all non gang users in data
* `-prep trim-home` - Trim home clusters in data
* `-prep trim-low-tw` - Trim tweets by low tweeting gangs
* `-prep trim-low-user` - Trim tweets by gangs with low users
* `-out border` - Generate all lines from polygon borders
* `-prep trim-lines` - Trim tweets near border lines
* `-prep trim-pols` - Trim tweets inside polygons

Generate results and output files:

* `-calc rnr|rivalnonrival` - Calculate rival-nonrival visit metrics
* `-calc rnr-dist|rivalnonrival-dist` - Calculate rival-nonrival visit metrics using distance norm
* `-out rnr|rivalnonrival` - Generate output for rival-nonrival metrics
* `-out rnr-dist|rivalnonrival-dist` - Generate output for rival-nonrival metrics using distance norm


Generate JSON files for `gambit-interface`:

* `-out visit-mat` - Generate visit matrix json
* `-out gang-tw` - Generate each gang\'s tweet count
* `-out rival-mat` - Generate rivalry matrix json
* `-out gang-loc` - Generate each gang\'s tweet locations
* `-out border` - Generate all lines from polygon borders


Test:

* `-see gang-tw` - See each gang\'s tweet count
* `-see test` - Call test function

---
#### License

Copyright (c) 2013 Nibir Bora, Vladimir Zaytsev.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this work except in compliance with the License.
You may obtain a copy of the License below, or at:

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---
	
	
