#!/usr/bin/env python
'''
TODO:
* deletion of temp
* -
* hideconsole parameter
* try to autofind rembg if path is not given

CHANGES
* Code cleanup
* New models
* Reordering of GUI
* Benchmark mode
* Safer usage of temp files - now they have unique name and deletion of temp 
  files deletes just temp file, not all fitting wildcard mask
* Removed losses of quality (originally Gimp exported to lossy JPEG and RemBG 
  after processing generated another lossy JPEG - now it's TIFF in both steps, 
  with nice compression/time balance - LZW)
'''

from gimpfu import *
import os, tempfile, time, pygtk
#import sys # for debug
pygtk.require('2.0')
import gtk

#sys.stderr = open( 'e:\\temp\\gimpstderr.txt', 'w') # for debug
#sys.stdout = open( 'e:\\temp\\gimpstdout.txt', 'w') # for debug
models = ("u2net","u2net_human_seg", "u2net_cloth_seg", "isnet-general-use")

def python_fu_RemoveBG(image, drawable, selModel, benchmark, asMask, alphaMatting, erodeSize):

	imageSize = drawable.width*drawable.height
	msg = "<span size=\"x-large\">Benchmarking using <b>\"%s\"</b> model on %d x %d image (<b>%d pix</b>)\r" % (models[selModel], drawable.width, drawable.height, imageSize)
	timerStart = time.clock()

	inPath = os.path.join(tempfile.gettempdir(), tempfile.mktemp() + ".tif")
	outPath = os.path.join(tempfile.gettempdir(), tempfile.mktemp() + "out.tif")

	x1 = 0
	y1 = 0
	option = ""

	image.undo_group_start()
	curLayer = pdb.gimp_image_get_active_layer(image)
	tmpImage = image
	tmpDrawable = drawable
	if pdb.gimp_selection_is_empty(image):
		pdb.file_tiff_save(image, drawable, inPath, inPath, 1)
	else:
		pdb.gimp_edit_copy(drawable)
		non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)
		tmpImage = gimp.Image(x2-x1, y2-y1, 0)
		tmpDrawable = gimp.Layer(tmpImage, "Temp", tmpImage.width, tmpImage.height, RGB_IMAGE, 100, NORMAL_MODE)
		pdb.gimp_image_add_layer(tmpImage, tmpDrawable, 0)
		pat = pdb.gimp_context_get_pattern()
		pdb.gimp_context_set_pattern("Leopard")
		pdb.gimp_drawable_fill(tmpDrawable, 4)
		pdb.gimp_context_set_pattern(pat)
		pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(tmpDrawable,TRUE))
		pdb.file_tiff_save(tmpImage, tmpDrawable, inPath, inPath, 1)
		pdb.gimp_image_delete(tmpImage)
		
	timerFile=time.clock()
	timeToLog = (timerFile - timerStart)*1000
	msg = msg + "File save time:\t<b><span foreground=\"#F73131\">%d</span></b> ms (<span foreground=\"#2FF972\">%d</span> pxpms*)\r" % (round(timeToLog), round(imageSize/timeToLog))
	aiExe = "C:\\Program Files (x86)\\Rembg\\rembg.exe" # SET YOUR PATH HERE
	if alphaMatting:
		option = "-a -ae %d" % (erodeSize)
	cmd = '""%s" i -m %s %s "%s" "%s""' % (aiExe, models[selModel], option, inPath, outPath)
	os.system(cmd)
	
	timerAI=time.clock()
	timeToLog = (timerAI - timerFile)*1000
	msg = msg + "AI processing time:\t<b><span foreground=\"#F73131\">%d</span></b> ms (<span foreground=\"#2FF972\">%d</span> pxpms*)\r" % (round(timeToLog), round(imageSize/timeToLog))
	
	if os.path.exists(outPath):
		newlayer = pdb.gimp_file_load_layer(image, outPath)
   		image.add_layer(newlayer, -1)
   		pdb.gimp_layer_set_offsets(newlayer, x1, y1)
   		if asMask:
   			pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE, newlayer)
   			image.remove_layer(newlayer)
			copyLayer = pdb.gimp_layer_copy(curLayer, TRUE)
			image.add_layer(copyLayer, -1)
			mask=copyLayer.create_mask(ADD_SELECTION_MASK)
			copyLayer.add_mask(mask)
			pdb.gimp_selection_none(image)

	image.undo_group_end()
	gimp.displays_flush()
	timeToLog = (time.clock() - timerStart)*1000
	msg = msg + "Total time:\t<b><span foreground=\"#F73131\">%d</span></b> ms (<span foreground=\"#2FF972\">%d</span> pxpms*)</span>\r\r\r<span size=\"medium\">* pxpms - pixels per millisecond</span>" % (round(timeToLog), round(imageSize/timeToLog))
	if benchmark==True:
		nicemsg(msg)

	os.remove(inPath)
	os.remove(outPath)

		
def nicemsg(message):
    dialog = gtk.Dialog("RemBG bridge", None, 0, (gtk.STOCK_OK, gtk.RESPONSE_OK))
    label = gtk.Label()
    label.set_markup(message)
    dialog.vbox.pack_start(label, True, True, 0)
    label.show()
    response = dialog.run()
    dialog.destroy()
	
	
register(
    "python_fu_RemoveBG",
    "Gimp->RemBG bridge",
    "rembg bridge",
    "krzysiu.net",
    "krzysiu.net",
    "2024",
    "<Image>/Filters/RemBG bridge...",
    "RGB*",
    [
		(PF_OPTION,"selModel", "Model", 0, models),
		(PF_TOGGLE, "benchmark", ("Benchmark mode - count execution time"), False),
		(PF_TOGGLE, "asMask", ("As Mask"), True),
		(PF_TOGGLE, "alphaMatting", ("Alpha matting"), False),
		(PF_SPINNER,"erodeSize", ("Matting erode size"), 15, (15,100,1))
    ],
    [],
    python_fu_RemoveBG,
    domain=("gimp20-python", gimp.locale_directory))

main()
