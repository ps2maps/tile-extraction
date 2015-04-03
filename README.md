# tile-extraction
These Python scripts are used to extract the [PlanetSide 2 Maps](http://ps2maps.com) continent map tiles from the game assets. The output from the game assets are .dds image files. This is the [DirectDraw Surface image format](http://en.wikipedia.org/wiki/DirectDraw_Surface).

The .dds tiles are then converted to JPGs and their latitude and longitude tile coordinates are converted to a system that is used by the Leaflet map for ps2maps.com.

ImageMagick is required for file conversion.

The script is for Windows but could easily be converted to run on Linux or OSX.
