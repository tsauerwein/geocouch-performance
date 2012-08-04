import os
import time
import random
import requests
import stat
import time

# Generates random query rectangles with a given aspect ratio and
# measures the time to execute the bounding-box queries with these
# rectangles.
# Additionally the number of leaf accesses for the queries is
# printed (the patch 'vtree-leaf-accesses.diff' has to be applied).

couch_url = "http://localhost:5985/"
database_name = "geocouch_benchmark"

area = (6.3, 48.8, 8.0, 50.4) # germany_location_selection
# area = (5.8, 47.2, 15.0, 55.0) # germany_location/water

number_of_queries = 500

# aspect ratio of the query rectangles
# height = aspect_ratio * width
aspect_ratio = 0.8

# Leaf-accesses log file
file = "/tmp/LeafAccesses.txt"

# build queries
xMin = area[0]
yMin = area[1]
xMax = area[2]
yMax = area[3]

# Maximum width of the query rectangle is 5% of the total width
area_width = 0.05 * (xMax - xMin)
# area_width = 0.1 * (xMax - xMin)

random_pos = random.Random(number_of_queries)
random_width = random.Random(number_of_queries)

query_rectangles = []
for i in range(0,number_of_queries):
    x = random_pos.uniform(xMin, xMax)
    y = random_pos.uniform(yMin, yMax)
    width = random_width.uniform(0, area_width)
    height = aspect_ratio * width
    
    query_rectangles.append((x, y, x + width, y + height))

# delete previous leaf-accesses file
if os.path.exists(file):
    os.remove(file)

# measure time to make the queries
print("Making queries ...")

start = time.time()

for rectangle in query_rectangles:
    queryBbox = "%.8f,%.8f,%.8f,%.8f" % (rectangle[0], rectangle[1], rectangle[2], rectangle[3])
    r = requests.get(couch_url + database_name + "/_design/benchmark/_spatial/justid?bbox=" + queryBbox + "&count=true")

time_difference = time.time() - start
print("%.f queries took %.5f seconds" %  (number_of_queries, time_difference))

# check if leaf accesses have been logged
try:
    with open(file) as f:
        # print time of last modification
        mod_time = os.stat(file)[stat.ST_MTIME]
        print("File '" +  file + "' was last modified at " + 
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(mod_time)))
        
        # calculate statistics
        count = 0
        leafAccessesTotal = 0
        for line in f:
            leafAccesses = int(line.strip())
            leafAccessesTotal += leafAccesses
            count += 1
        
        print("Number of queries: %d" % count)
        print("Total leaf accesses: %d" % leafAccessesTotal)
        print("Avg. leaf accesses per query: %.2f" % (float(leafAccessesTotal)/count))
except IOError as e:
    print("Leaf accesses have not been tracked in '" + file + "'")


#curl -X GET 'http://localhost:5985/geocouch_benchmark/_design/benchmark/_spatial/justid?bbox=0,0,0,0'

