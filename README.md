# rembg-gimp-alt
Modernized remBG bridge for Gimp. Bases on the original work of elastic192 (https://elastic192.blogspot.com/2022/06/gimp-ai-rembg.html). 

## Installation
1. Follow rembg.exe installation guide that could be found at https://github.com/danielgatis/rembg
2. Set your path to RemBG CLI (`rembg.exe`) in line 67 of `RemoveBG.py`
3. Copy `RemoveBG.py` to your Gimp plugin directory
4. Restart Gimp
5. Start using `Filters>RemBG brigde...`

## Changes in code 
* Code cleanup
* Support for new models
* Reordering of GUI
* Benchmark mode
* Safer usage of temp files - now they have unique name and deletion of temp files deletes just temp file, not all fitting wildcard mask
* Removed losses of quality (originally Gimp exported to lossy JPEG and RemBG after processing generated another lossy JPEG - now it's TIFF in both steps, with nice compression/time balance - LZW)
