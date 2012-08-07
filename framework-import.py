import os
import time
import requests
import rectangle_file_reader

# Small script that imports data files of the test framework
# developed for the evaluation of the RR*-Tree.
#
# The data can be downloaded under this URL:
#	http://www.mathematik.uni-marburg.de/~achakeye/data/data/
# A description of the data sets is available here:
#	http://www.mathematik.uni-marburg.de/~rstar/benchmark/distributions.pdf
#

couch_url = "http://localhost:5985/"

prefix = "org_"
imports = [
	 (prefix + "abs02", "data/framework/abs02.rec")	# Absolute
	,(prefix + "bit02", "data/framework/bit02.rec")	# Bit
	,(prefix + "dia02", "data/framework/dia02.rec")	# Diagonal
	,(prefix + "par02", "data/framework/par02.rec")	# Parcel
	,(prefix + "ped02", "data/framework/ped02.rec")	# P-edges
	,(prefix + "pha02", "data/framework/pha02.rec")	# P-haze
	,(prefix + "rea02", "data/framework/rea02.rec")	# CaliforniaStreets
	,(prefix + "uni02", "data/framework/uni02.rec")	# ?
]

# number of documents that are inserted at once
chunk_size = 500


def import_file(database_name, rectangle_file):
	# read rectangles from file
	limit = 500
	(rectangles, count) = rectangle_file_reader.read_rectangles(rectangle_file, limit=limit)

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

def send(chunk):
	docs = []

	for doc in chunk:
		(index, rectangle) = doc
		(xMin, yMin, xMax, yMax) = rectangle

		if xMin == xMax and yMin == yMax:
			# import points as points
			geometry = '"geometry":{"type": "Point", "coordinates": [%.10f, %.10f]}' % (xMin, yMin)
		else:
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

for (database_name, rectangle_file) in imports:
	import_file(database_name, rectangle_file)
	print()
	print("-------------------------------------")
	print()


#curl -X GET 'http://localhost:5985/geocouch_benchmark/_design/benchmark/_spatial/justid?bbox=0,0,0,0&count=true'

