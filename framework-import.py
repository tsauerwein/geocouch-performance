import os
import time
import xdrlib
import requests

# Small script that imports data files of the test framework
# developed for the evaluation of the RR*-Tree.
#
# The data can be downloaded under this URL:
#	http://www.mathematik.uni-marburg.de/~achakeye/data/data/
# A description of the data sets is available here:
#	http://www.mathematik.uni-marburg.de/~rstar/benchmark/distributions.pdf
#

couch_url = "http://localhost:5985/"
database_name = "geocouch_benchmark"

rectangle_file = "data/framework/abs02.rec"	# Absolute
# rectangle_file = "data/framework/bit02.rec"	# Bit
# rectangle_file = "data/framework/dia02.rec"	# Diagonal
# rectangle_file = "data/framework/par02.rec"	# Parcel
# rectangle_file = "data/framework/ped02.rec"	# P-edges
# rectangle_file = "data/framework/pha02.rec"	# P-haze
# rectangle_file = "data/framework/rea02.rec"	# CaliforniaStreets
# rectangle_file = "data/framework/uni02.rec"	# ?

# number of documents that are inserted at once
chunk_size = 500

def main():
	# read rectangles from file
	file = open(rectangle_file, "rb")
	data = file.read()
	unpacker = xdrlib.Unpacker(data)

	print("Reading input file...")
	rectangles = []
	count = 0
	try:
		# while True:
		for x in range(0,20):
			xMin = unpacker.unpack_double()
			yMin = unpacker.unpack_double()
			xMax = unpacker.unpack_double()
			yMax = unpacker.unpack_double()

			rectangles.append((xMin, yMin, xMax, yMax))
			count += 1
	except xdrlib.Error as error:
		raise Exception("Error reading file", error.msg)
	except EOFError:
		print("Reached end of file")
	file.close()

	print("Read %d rectangles" % (count))

	# drop existing database
	r = requests.delete(couch_url + database_name)
	print("Trying to delete existing database: " + r.text)

	# create database
	r = requests.put(couch_url + database_name)
	print("Creating database '" + database_name + "': " + r.text)

	if r.status_code != 201:
		raise Exception('Could not create database') 

	# insert rectangles in chunks
	chunk = []
	current_chunk_size = 0

	index = 0
	for rectangle in rectangles:
		chunk.append((index, rectangle))
		current_chunk_size += 1
		index += 1

		if current_chunk_size >= chunk_size:
			send(chunk)
			chunk = []
			current_chunk_size = 0

	# send remaining rectangles
	if current_chunk_size >= 0:
		send(chunk)

	# add spatial view that simply returns the document id
	r = requests.put(couch_url + database_name + "/_design/benchmark", 
		data='{\"spatial\":{\"justid\":\"(function(doc) { if (doc.geometry) { emit(doc.geometry, doc._id);}})\"}}')
	print("Adding spatial view '" + database_name + "': " + r.text)

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

def send(chunk):
	docs = []

	for doc in chunk:
		index = doc[0]
		xMin = doc[1][0]
		yMin = doc[1][1]
		xMax = doc[1][2]
		yMax = doc[1][3]

		lowerLeft = "[%.10f, %.10f]" % (xMin, yMin)
		lowerRight = "[%.10f, %.10f]" % (xMax, yMin)
		upperRight = "[%.10f, %.10f]" % (xMax, yMax)
		upperLeft = "[%.10f, %.10f]" % (xMin, yMax)

		geometry = '"geometry":{"type": "Polygon", "coordinates": [[' + \
lowerLeft + "," + lowerRight + "," + upperRight + "," + upperLeft + "," + lowerLeft + "]]}"

		id = '"_id": "%010d"' % index

		json_doc = '{' + id + ',' + geometry + '}'

		docs.append(json_doc)
		# print(json_doc)

	docs_json = ",".join(docs)
	body = '{"docs":[' + docs_json + ']}'

	r = requests.post(couch_url + database_name + "/_bulk_docs", 
		data=body, 
		headers={'content-type': 'application/json'})

	if r.status_code != 201:
		raise Exception('Adding documents failed', r.text) 

main()


#curl -X GET 'http://localhost:5985/geocouch_benchmark/_design/benchmark/_spatial/justid?bbox=0,0,0,0&count=true'

