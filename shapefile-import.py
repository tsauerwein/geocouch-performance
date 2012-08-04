import time
import requests
import os

# Small script that measures the time to build a R-Tree for
# a Shapefile, that is imported with shp2geocouch.

couch_url = "http://localhost:5985/"
database_name = "geocouch_benchmark"

shp_file_name = "data/germany.shapefiles/germany_location_selection_7/germany_location.shp"
# shp_file_name = "data/germany.shapefiles/germany_location.shp"

# path to shp2geocouch
shp2geocouch_bin = "./shp2geocouch/bin/shp2geocouch"

# drop database
r = requests.delete(couch_url + database_name)
print("Trying to delete existing database: " + r.text)

# load shapefile with shp2geocouch
print("Importing " + shp_file_name)
os.system(shp2geocouch_bin + " " + shp_file_name + " " + couch_url + database_name)

# add spatial view that simply returns the document id
r = requests.put(couch_url + database_name + "/_design/benchmark",
	data='{\"spatial\":{\"justid\":\"(function(doc) { if (doc.geometry) { emit(doc.geometry, doc._id);}})\"}}')
print("Adding spatial view '" + database_name + "/_design/benchmark" + "': " + r.text)

if r.status_code != 201:
	raise Exception('Could not add spatial view')

# measure time to build the R-Tree
print("Started building R-Tree at " +
    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " ...")
start = time.time()
r = requests.get(couch_url + database_name + "/_design/benchmark/_spatial/justid?bbox=0,0,0,0&count=true")
time_difference = time.time() - start

print("Building R-Tree took %.5f seconds" %  time_difference)
print("Finished at " +
    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

#curl -X GET 'http://localhost:5985/geocouch_benchmark/_design/benchmark/_spatial/justid?bbox=0,0,0,0'

