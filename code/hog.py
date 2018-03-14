import cv2
import matplotlib.pyplot as plt
from skimage.feature import hog
from skimage import data, color, exposure
import os
import glob
import json
import numpy as np

isExists = os.path.exists('develop')
meta_dump = {}

if not isExists:
    os.makedirs('develop')
folders = glob.glob('screenshot1' + "/**")
for w in folders:
    for infile in sorted(sorted(glob.glob(w + "/stoat_fsm_output/ui/*.xml"), reverse=True), key=len, reverse=True):
        pngfile = infile.replace(".xml", ".png")
        if os.path.exists(pngfile) and os.stat(pngfile).st_size > 0:
            widget = {}
            im = cv2.imread(pngfile)
            gr = im
            if im is not None:
                gr = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            image = gr
            fd, hog_image = hog(image, orientations=8, pixels_per_cell=(16, 16),
			 	                    cells_per_block=(1, 1), visualise=True, block_norm='L2-Hys')
            #print(np.amax(fd))
            fd = fd / np.amax(fd)
            hog_image = hog_image / np.amax(hog_image)
            #print(hog_image.shape)
            widget['hog_fd'] = fd.tolist()
            widget['hog_image'] = hog_image.tolist()
            meta_dump[pngfile] = widget
with open(os.path.join('develop', "meta_dump.txt"), "a+") as f:
    json.dump(meta_dump, f, sort_keys=True, indent=3, separators=(',', ': '))
