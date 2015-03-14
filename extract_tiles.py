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

root=sys.path[0]+"/"
targetfolder=root+"output/"

# PlanetSide 2 installation Assets folder
inputfolder = "C:/PlanetSide2/Resources/Assets/"

# ImageMagick Convert exe
convert = "C:/ImageMagick/convert.exe"

# List of continents to extract tiles for
continents = ['indar']

if os.path.exists(targetfolder):
	print "Deleting output folder"
	shutil.rmtree(targetfolder)
time.sleep(1)
os.mkdir(targetfolder)

print "Extracting map tiles",
if len(continents) > 0:
	print "for " + ", ".join(continents)

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
		if extension == 'dds' and filename.find('_lod0') != -1:

			if len(continents) > 0:
				# Find specified continents
				continentFound = False
				for continent in continents:
					if filename.find(continent.lower()) != -1:
						continentFound = True
						break
				if continentFound == False:
					continue;

			print '.',

			# Convert the tile coordinates
			fileparts = filename.replace('_lod0','').replace('_tile','').split('_')
			continent = fileparts[0]
			longitude = str(int(fileparts[1])/4)
			latitude = str((int(fileparts[2]) * -1)/4 - 1)

			# Output filename (zoom level 5 is base zoom value)
			outputFilename = "tile_5_" + longitude + "_" + latitude + ".jpg"

			# Write temp DDS file
			tmp = targetfolder + ent.name.lower()
			dds=open(tmp,"wb")
			dds.write(pack.read(ent.size))
			dds.close()

			# Convert to PNG
			cmd = convert + " " + tmp + " -flip -quality 85 " + targetfolder + outputFilename
			os.system(cmd)

			# Delete the tmp DDS file
			os.remove(tmp)

	pack.close()
	ij+=1
