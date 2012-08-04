geocouch-performance
====================
This project contains scripts to evaluate the performance of [GeoCouch](https://github.com/couchbase/geocouch). It consists of two parts:

* Script `shapefile-import.py` and `shapefile-query-time.py` allow to import Shapefiles into GeoCouch and to run random bounding-box queries on the created database.

* Script `framework-import.py` and `framework-query-time.py` provide support for 
  the test framework developed for the evaluation of the 
  [RR*-Tree](http://dl.acm.org/citation.cfm?id=1559929). The test framework consists
  of artificial and real data sets and three range-query sets for each data set. A 
  description of the data can be found in 
  ["A Benchmark for Multidimensional Index Structures (PDF)"](http://www.mathematik.uni-marburg.de/~rstar/benchmark/distributions.pdf).
  
  The framework data sets can be downloaded [here](http://www.mathematik.uni-marburg.de/~achakeye/data/data). 
  The query sets are available under [query_1](http://www.mathematik.uni-marburg.de/~achakeye/data/query_1/), 
  [query_100](http://www.mathematik.uni-marburg.de/~achakeye/data/query_100/) and 
  [query_1000](http://www.mathematik.uni-marburg.de/~achakeye/data/query_1000/).

Usage
------
The scripts require the library [requests](http://requests.readthedocs.org/) and were developed with Python 3.

The variables at the top of the scripts allow to define the CouchDB URL, the database name and the data sets. Then the scripts can be run with:

    python3 shapefile-import.py
    python3 shapefile-query-time.py