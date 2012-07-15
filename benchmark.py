import os
import time

# Small script that measures the time to build a R-Tree for
# a Shapefile, that is imported with shp2geocouch.

couch_url = "http://localhost:5985/"
database_name = "geocouch_benchmark"

#shp_file_name = "data/germany.shapefiles/germany_location_selection/germany_location.shp"
shp_file_name = "data/germany.shapefiles/germany_location.shp"

# path to shp2geocouch
shp2geocouch_bin = "./shp2geocouch/bin/shp2geocouch"

# drop database
os.system("curl -X DELETE " + couch_url + database_name)

# load shapefile with shp2geocouch
print("Importing " + shp_file_name)
os.system(shp2geocouch_bin + " " + shp_file_name + " " + couch_url + database_name)

# add spatial view that simply returns the document id
os.system("curl -X PUT -d '{\"spatial\":{\"justid\":\"(function(doc) { if (doc.geometry) { emit(doc.geometry, doc._id);}})\"}}' " + couch_url + database_name + "/_design/benchmark")

# measure time to build the R-Tree
print("Started building R-Tree at " +
    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " ...")
start = time.time()
os.system("curl -X GET '" + couch_url + database_name + "/_design/benchmark/_spatial/justid?bbox=0,0,0,0'")
time_difference = time.time() - start

print("Building R-Tree took %.5f seconds" %  time_difference)
print("Finished at " +
    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

#curl -X GET 'http://localhost:5985/geocouch_benchmark/_design/benchmark/_spatial/justid?bbox=0,0,0,0'

