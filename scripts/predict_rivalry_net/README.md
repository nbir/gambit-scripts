# Gambit - Research scripts [predictRivalryNetwork]


Research scripts for [Gambit](http://brain.isi.edu/~gambit/v2.0/)
| [Computational Behavior Group](http://cbg.isi.edu)
| USC Information Sciences Institute, 4676 Admiralty Way, Marina del Rey, CA 90292

## Contributors

* [Nibir Bora](http://nibir.me/) | <nbora@usc.edu>
* [Vladimir Zaytsev](http://zvm.me/) | <zaytsev@usc.edu>


## Input files

All input files should be inside the sub-directory `data/<choosen_data_folder>/`.

Names in settings.py:
* `HBK_TWEET_LOC_FILE` - CSV file with all collected tweets. Each row: `<user_id, lat, lng>`


Hardcoded:

* `pickle/visit_mat.pickle` - Visit matrix with unnormalized counts.
* `pickle/visit_mat_norm.pickle` - Visit matrix with normalized counts.


## Run directives

Format: `python run.py -<option> <parameters>`

Prepare data:

* `--prep trim-visit-mat` - Trim visit matrix for min tweet bound

Generate results and output files:


Test:

* `--see test` - Call test function

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
	
	
