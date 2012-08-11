import time
import stat
import time
import os
import requests
import rectangle_file_reader

# Reads query files from the RR*-Tree evaluation framework and
# measures the time to execute the bounding-box queries with these
# rectangles.
# Additionally the number of leaf accesses for the queries is
# printed (the patch 'vtree-leaf-accesses.diff' has to be applied).
#
# The data can be downloaded under these URLs:
#   http://www.mathematik.uni-marburg.de/~achakeye/data/query_1/
#   http://www.mathematik.uni-marburg.de/~achakeye/data/query_100/
#   http://www.mathematik.uni-marburg.de/~achakeye/data/query_1000/
# A description of the data sets is available here:
#   http://www.mathematik.uni-marburg.de/~rstar/benchmark/distributions.pdf
#

couch_url = "http://localhost:5985/"

# query_type = "query_1"        # avg. 1 result per query
query_type = "query_100"      # avg. 100 results per query
# query_type = "query_1000"     # avg. 1000 results per query

prefix = "ext_"
queries = [
    # (database_name, dataset_name)
     (prefix + "abs02", "abs02")    # Absolute
    ,(prefix + "bit02", "bit02")    # Bit
    ,(prefix + "dia02", "dia02")    # Diagonal
    ,(prefix + "par02", "par02")    # Parcel
    # ,(prefix + "ped02", "ped02")   # P-edges (file invalid)
    ,(prefix + "pha02", "pha02")    # P-haze
    ,(prefix + "rea02", "rea02")    # CaliforniaStreets
    ,(prefix + "uni02", "uni02")    # ?
]

def run_queries(database_name, dataset):
    queries_file = "data/framework-queries/" + query_type + "/" + dataset + ".rec"

    # Leaf-accesses log file
    file = "/tmp/LeafAccesses.txt"

    limit = None
    (query_rectangles, count) = rectangle_file_reader.read_rectangles(queries_file, limit=limit)
    print("Read %d query rectangles" % (count))

    # delete previous leaf-accesses file
    if os.path.exists(file):
        os.remove(file)

    # measure time to make the queries
    print("Making queries ...")

    start = time.time()

    for rectangle in query_rectangles:
        (xMin, yMin, xMax, yMax) = rectangle
        queryBbox = "%.10f,%.10f,%.10f,%.10f" % (xMin, yMin, xMax, yMax)

        r = requests.get(couch_url + database_name + "/_design/benchmark/_spatial/justid?bbox=" + queryBbox + "&count=true")

    time_difference = time.time() - start
    print("%.f queries took %.5f seconds" %  (count, time_difference))

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

for (database_name, dataset) in queries:
    run_queries(database_name, dataset)
    print()
    print("-------------------------------------")
    print()


#curl -X GET 'http://localhost:5985/geocouch_benchmark/_design/benchmark/_spatial/justid?bbox=0,0,0,0&count=true'
