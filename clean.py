import re

with open("output.txt") as h:
	lineiter = iter(h.read().split("\n"))

while True:
	try:
		currentline=next(lineiter)
		ip=currentline.split(" ")[3]
		with open("combo.txt", "a+") as h:
			h.write(ip+"\n")
			h.close()
	except StopIteration:
		break
	except Exception as e:
		pass