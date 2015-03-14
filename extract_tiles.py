## Credit to RoyAwesome for figuring out the .pack file format.
## Documentation on this format is in these comments at the top
##
## file is in big endian
##
## a pack file has several parts which are all identical in structure.
## there is no global header. not even magic
##
##
## START OF ONE PACK FILE PART
##
## metadata section (0x2000 bytes):
##	uint32: absolute offset for the next part of the pack file (end of current part)
##		if last pack part: 00000000
##	uint32: number of entries
##
##	strings prefixed with uint32 length, no trailing zero!
##	3 uint32 after the string
##		1 absolute offset (this can be in another pack part)
##		2 length
##		3 crc32 of the payload
##
##	padding so the section has 0x2000 bytes
##
##
## payload section (trivial)

from struct import unpack,pack
import sys, os, shutil, math, time, random, subprocess

def ps2int(num):
	intstr=str(num)
	if len(intstr)==1:   return "00"+intstr
	elif len(intstr)==2: return"0"+intstr
	else:                return intstr

class entry:
	pass

output = sys.path[0] + "/output/"

# PlanetSide 2 installation Assets folder
inputfolder = "C:/PlanetSide2/Resources/Assets/"

# JPG Quality
quality = str(85)

# ImageMagick exe's
convert = "C:/ImageMagick/convert.exe"
montage = "C:/ImageMagick/montage.exe"

# List of continents to extract tiles for
continents = ['indar']

# Loop thru continents
for continent in continents:

	# Delete and recreate output folder
	if os.path.exists(output + continent):
		print "Deleting output folder for " + continent
		shutil.rmtree(output + continent)
		time.sleep(1)

	print "Extracting zoom level 5 tiles for " + continent

	# Create output folders
	zoom5 = output + continent + "/zoom5/"
	os.makedirs(zoom5)
	zoom4 = output + continent + "/zoom4/"
	os.makedirs(zoom4)
	zoom3 = output + continent + "/zoom3/"
	os.makedirs(zoom3)
	zoom2 = output + continent + "/zoom2/"
	os.makedirs(zoom2)
	zoom1 = output + continent + "/zoom1/"
	os.makedirs(zoom1)
	zoom0 = output + continent + "/zoom0/"
	os.makedirs(zoom0)

	ij=0
	while 1:
		partSize=1 #anything non-zero to make a do-while
		entrylist=[]
		fname=inputfolder+"Assets_"+ps2int(ij)+".pack"
		if not os.path.exists(fname):
			break
		pack = open(fname,"rb")
		while partSize:
			partSize=unpack(">I",pack.read(4))[0]
			numEntries=unpack(">I",pack.read(4))[0]
			for i in xrange(numEntries):
				ent=entry()
				stringlen=unpack(">I",pack.read(4))[0]
				ent.name=pack.read(stringlen)
				ent.offset,ent.size,ent.crc32=unpack(">III",pack.read(12))
				entrylist.append(ent)

			end=entrylist[-1].offset+entrylist[-1].size
			pack.seek(partSize)

		for ent in entrylist:
			pack.seek(ent.offset)
			pathinfo = os.path.splitext(ent.name)
			extension = pathinfo[1][1:].lower()
			filename = pathinfo[0].lower()

			# Find map tiles
			if extension == 'dds' and filename.find('_lod0') != -1 and filename.find(continent) != -1:

				print '.',

				# Convert the tile coordinates
				fileparts = filename.replace('_lod0','').replace('_tile','').split('_')
				longitude = str(int(fileparts[1])/4)
				latitude = str((int(fileparts[2]) * -1)/4 - 1)

				# Output filename (zoom level 5 is base zoom value)
				outputFilename = continent + "_5_" + longitude + "_" + latitude + ".jpg"

				# Write temp DDS file
				tmp = zoom5 + ent.name.lower()
				dds=open(tmp,"wb")
				dds.write(pack.read(ent.size))
				dds.close()

				# Convert to PNG
				cmd = convert + " " + tmp + " -flip -quality " + quality + " " + zoom5 + outputFilename
				os.system(cmd)

				# Delete the tmp DDS file
				os.remove(tmp)

		pack.close()
		ij+=1

	# Create Zoom Level 4 tiles
	# Combines 4 tiles into one in mosaic pattern
	print "Extracting zoom level 4 tiles for " + continent

	for x in range(-16,16):
		if x%2 == 0:
			for y in range(-16,16):
				if y%2 == 0:

					tile1 = zoom5 + continent + "_5_" + str(x) + "_" + str(y) + ".jpg"
					tile2 = zoom5 + continent + "_5_" + str(x+1) + "_" + str(y) + ".jpg"
					tile3 = zoom5 + continent + "_5_" + str(x) + "_" + str(y+1) + ".jpg"
					tile4 = zoom5 + continent + "_5_" + str(x+1) + "_" + str(y+1) + ".jpg"

					outputFilename = continent + "_4_" + str(x/2) + "_" + str(y/2) + ".jpg"

					cmd = montage + " -geometry +0+0 -background none -quality " + quality + " " + tile1 + " " + tile2 + " " + tile3 + " " + tile4 + " " + zoom4 + outputFilename
					os.system(cmd)

