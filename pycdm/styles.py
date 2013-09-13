
def colormap(filename):
	
	try:
		lines = open(filename).readlines()
	except:
		print "Can't open colormap file %s" % (filename)
		
	map = []
	
	
	for line in lines[:-1]:
		fields = line.split()
		r, g, b = int(fields[2]), int(fields[3]), int(fields[4])
		
		map.append((r, g, b))
		
	return map

def mapcolor(value, min, max, map):
	
	if (value < min):
		return map[0]
		
	if (value > max):
		return map[-1]
		
	return map[int(len(map) * (value-min)/(max-min))]
