from PIL import Image, ImageOps
import os, sys

def invert(file):
	image = Image.open(file)
	ImageOps.invert(image.convert('RGB')).save(file)
	print(f"Inverted {file}...")



if len(sys.argv) > 1:
	path = sys.argv[1]
	if os.path.isdir(path):
		for i in os.listdir(path):
			try:
				invert(i)
			except:
				print(f"Unable to invert {i}...")
	else:
		invert(path)
