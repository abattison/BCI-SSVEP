import sys

for filename in sys.argv[1:]:
	f = open(filename,"r")
	lines = f.readlines()
	f.close()
	i = 0
	f = open(filename[:-4]+"_fixed.dat", "w")
	for line in lines:  
		i += 1
		if i < 58:
			continue
		elif i == 58:
			f.write("471 520 2\n")
		else:
			f.write(line)
	f.close()
