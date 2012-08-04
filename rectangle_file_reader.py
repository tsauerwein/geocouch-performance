import xdrlib

def read_rectangles(rectangle_file, limit=None):
	file = open(rectangle_file, "rb")
	data = file.read()
	unpacker = xdrlib.Unpacker(data)

	print("Reading input file '" + rectangle_file + "'...")
	rectangles = []
	count = 0
	try:
		while True:
			if limit is not None and count >= limit:
				break;

			xMin = unpacker.unpack_double()
			yMin = unpacker.unpack_double()
			xMax = unpacker.unpack_double()
			yMax = unpacker.unpack_double()

			rectangles.append((xMin, yMin, xMax, yMax))
			# print("%.10f,%.10f,%.10f,%.10f" % (xMin, yMin, xMax, yMax))
			count += 1
	except xdrlib.Error as error:
		raise Exception("Error reading file", error.msg)
	except EOFError:
		print("Reached end of file")
	file.close()

	return (rectangles, count)