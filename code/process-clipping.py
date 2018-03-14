import argparse
import os
import glob
import string
import re
import shutil
import progressbar
import json
import numpy as np
import hashlib
import time
import itertools

from PIL import Image, ImageFile, ImageDraw, ImageFont
Image.LOAD_TRUNCATED_IMAGES = True
from lxml import etree
from multiprocessing import Pool, Value, Manager
from collections import deque
from colorthief import ColorThief

import cv2
import matplotlib.pyplot as plt
from skimage.feature import hog
from skimage import data, color, exposure

import sys
# sys.path.append("C:\Users\user\colory")
# from colors import Color
from colour import Color



parser = argparse.ArgumentParser()
parser.add_argument("--input_dir", required=True, help="path to folder containing app packages")
a = parser.parse_args()

cwd = os.getcwd()
archive_dir = cwd + "/widget_clippings"

target_list = ["TextView","Button", "ImageButton", "CompoundButton", "ProgressBar", "SeekBar", "Chronometer", "View", "CheckBox", "RadioButton", "Switch", "EditText", "ToggleButton", "RatingBar", "Spinner"]


def checkFileValidity(inputFile):
	'''
	Check the validity of the XML file and ignore it if possible
	Due to the unknown reasons, the content in some XML file is repetative or
	'''
	homeScreen_list = ["Make yourself at home", "You can put your favorite apps here.", "To see all your apps, touch the circle."]
	unlockHomeScreen_list = ["Camera", "[16,600][144,728]", "Phone", "[150,1114][225,1189]", "People", "[256,1114][331,1189]", "Messaging", "[468,1114][543,1189]", "Browser", "[574,1114][649,1189]"]
	browser = ["com.android.browser:id/all_btn", "[735,108][800,172]", "com.android.browser:id/taburlbar", "com.android.browser:id/urlbar_focused"]
	with open(inputFile) as f:
		content = f.read()
		#it is the layout code for the whole window and no rotation
		if 'bounds="[0,0][800,1216]"' in content and '<hierarchy rotation="1">' not in content:
			if not all(keyword in content for keyword in browser) and not all(keyword in content for keyword in homeScreen_list) and not all(keyword in content for keyword in unlockHomeScreen_list):
				#it should not be the homepage of the phone
				bounds_list = re.findall(r'bounds="(.+?)"', content)
				if len(bounds_list) < 2:
					return False
				#if float(len(bounds_list)) / len(set(bounds_list)) < 1.2:   #so far, we do not check this option
					#print len(text_list), len(set(text_list)), inputFile.split("\\")[-1]
				return True

	return False

def checkDuplicateFile(inputFile):
	with open(inputFile) as f:
		global hash_dict
		content = f.read()
		content = re.sub(r'(?!.*\/>).*', "", content)
		content = re.sub(r'\s', "", content)
		content = re.sub(r'content-desc=".*?"', "", content)  #remove the filled text
		content = re.sub(r'text=".*?"', "", content)  #remove the text
		content = re.sub(r'bounds=".*?"', "", content)
		content = re.sub(r'index=".*?"', "", content)
		content = re.sub(r'NAF=".*?"', "", content)
		content = re.sub(r'focused=".*?"', "", content)
		fileHash = hashlib.sha224(content).hexdigest()       #get the hash digest of the file
		if fileHash not in hash_dict:
			hash_dict[fileHash] = ""
			return True
		else:
			return False


def getDimensions(coor_from, coor_to):
	dim = {}
	dim['width'] = coor_to[0] - coor_from[0]
	dim['height'] = coor_to[1] - coor_from[1]
	return dim

def createClipping(path_to_png, coor_from, coor_to, count):
	filename = os.path.basename(path_to_png)
	im = Image.open(path_to_png)
	clip = im.crop((coor_from[0], coor_from[1], coor_to[0], coor_to[1]))
	clip.save(os.path.join(archive_dir, "%s-clippings-%s.png" %(filename, count)))
	color_thief = ColorThief(path_to_png)
	#dominant_color = color_thief.get_color(quality=1)
	palette = color_thief.get_palette(color_count=6)
	return palette

def createClippings(widgets_folder, meta_dump, further_remove):
	global count

	#meta_dump = {}
	#meta_dump[folder_name] = {}
	for w_type, widgets in widgets_folder.items():
		#meta_dump[w_type] = {}
		for widget in widgets:
			widget_dir = os.path.join(archive_dir, w_type)
			duplicate = False
			#print(widget_dir)
			try:
				im = Image.open(widget['src'] + ".png")
				clip = im.crop((widget['coordinates']['from'][0], widget['coordinates']['from'][1], widget['coordinates']['from'][0]+widget['dimensions']['width'], widget['coordinates']['from'][1]+widget['dimensions']['height']))
			except OSError as err:
				print widget['src']
				print "[-] OSError - " + str(err)
				continue
			except IndexError as err:
				print widget['src']
				print "[-] IndexError - " + str(err)
				print "[-] " + w_type + "-" + widget['src']
				print "[-] " + str(widget['coordinates'])
				print "[-] " + str(widget['dimensions'])
				continue
			except IOError as err: #image file is truncated
				print widget['src']
				print "[-] IOError - " + str(err)
				continue

			filename = "clipping-" + str(count.value)
			filepath = os.path.join(widget_dir, filename + ".png")
			#print(filepath)
			if not os.path.exists(widget_dir):
				os.makedirs(widget_dir)
			clip.save(filepath)
			imA = Image.open(os.path.join(widget_dir, filename + ".png"))
			hA = imA.histogram()
			widget['hot'] = hA

			im = cv2.imread(filepath)
			print(im)
			gr = im
			if im is not None:
				gr = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
			#print(im.shape)

			image = gr
			fd, hog_image = hog(image, orientations=8, pixels_per_cell=(16, 16),
			 	                    cells_per_block=(1, 1), visualise=True, block_norm='L2-Hys')
			widget['hog_fd'] = fd.tolist()
			widget['hog_image'] = hog_image.tolist()
			# try:
			# 	fd, hog_image = hog(image, orientations=1, pixels_per_cell=(1, 1),
			# 	                    cells_per_block=(1, 1), visualise=True, block_norm='L2-Hys')
			# 	widget['hog_fd'] = fd
			# 	widget['hog_image'] = hog_image
			# except Exception as e:
			# 	#print("hi2")
			# 	os.remove(filepath)
			# 	continue


			try:
				color_thief = ColorThief(filepath)
				# get the dominant color
				dominant_color = color_thief.get_color(quality=1)
				#widget['color'] = dominant_color
				# print(dominant_color)
				# print(type(dominant_color))
				# print(type(getColor(dominant_color)))
				# print(widget['color'])
				widget['color'] = getColor(dominant_color)
				#print("hi1")
			except Exception as e:
				#print("hi2")
				os.remove(filepath)
				continue

			if not meta_dump[w_type]:
				meta_dump[w_type][filename] = widget
				with count.get_lock():
					count.value += 1
				#n1 = final_stats[w_type]
				#n1[2] += 1
				#final_stats.pop(w_type, None)
				#final_stats[w_type] = n1
				further_remove[w_type] += 1
			else:
				for key in meta_dump[w_type].keys():
					diff_score = compareHisto(os.path.join(widget_dir, key + ".png"), os.path.join(widget_dir, filename + ".png"))
					if diff_score < 0.13:
						os.remove(os.path.join(widget_dir, filename + ".png"))
						duplicate = True
						break

				if not duplicate:
					meta_dump[w_type][filename] = widget
					with count.get_lock():
						count.value += 1
					#n2 = final_stats[w_type]
					#n2[2] += 1
					#final_stats.pop(w_type, None)
					#final_stats[w_type] = n2
					further_remove[w_type] += 1

	return further_remove
	#with open(os.path.join(archive_dir, "meta_dump.txt"), "a+") as f:
	#json.dump(meta_dump, f)
	#json.dump(meta_dump, f, sort_keys=True, indent=3, separators=(',', ': '))




def remove_overlap_duplicates(widgets, widgets_folder):
	#drawer = ["drawer", "nav",]
	global stats


	widgets.reverse()
	layout = np.zeros((801,1217), dtype=np.int)
	for idx, widget in enumerate(widgets):
		overlap = False
		starti = widget['coordinates']['from'][0] + 1
		endi = widget['coordinates']['to'][0] - 1
		startj = widget['coordinates']['from'][1] + 1
		endj = widget['coordinates']['to'][1] - 1

		'''for i in range(starti, endi + 1):
			for j in range(startj, endj + 1):
				if layout[i][j] == 1:
					if widget['leaf']:
						overlap = True
						layout[i][j] = -1
				elif layout[i][j] == -1:
					overlap = True
				elif layout[i][j] == 2:
					if widget['leaf']:
						overlap = True
						layout[i][j] = -1
				else:
					if widget['leaf']:
						layout[i][j] = 1
					else:
						layout[i][j] = 2'''
		for i in range(starti, endi + 1):
			for j in range(startj, endj + 1):
				if layout[i][j] == 1:
					if widget['leaf']:
						overlap = True
						layout[i][j] = -1
				elif layout[i][j] == -1:
					overlap = True
				elif layout[i][j] == 2:
					if widget['leaf']:
						overlap = True
						layout[i][j] = -1
				else:
					if widget['leaf']:
						layout[i][j] = 1
					else:
						layout[i][j] = 2

		#print "[*]" + str(overlap), widget['class'], widget['coordinates']
		#if any(d in widget['resource-id'] for d in drawer) and widget['coordinates']['from'][0] == 0 and widget['coordinates']['from'][1] == 33 and 373 <= widget['coordinates']['to'][0] <= 533 and widget['coordinates']['to'][1] == 1216:

		if overlap == True:
			#draw.rectangle((widget['coordinates']['from'], widget['coordinates']['to']), outline="blue")
			#draw.text(widget['coordinates']['from'], widget['widget_class'], font=fnt, fill="blue")
			continue
		else:
			if widget['leaf'] and widget['widget_class'] in target_list:
				if widget['widget_class'] == "View" and not(widget['clickable'] == "true" and widget['focusable'] == "true"):
					continue
				if not widgets_folder[widget['widget_class']]:
					#widgets_folder.append(widget)
					widgets_folder[widget['widget_class']].append(widget)
					n1 = stats[widget['widget_class']]
					n1[1] += 1
					#stats.pop(widget['widget_class'], None)
					stats[widget['widget_class']] = n1
				else:
					duplicate = False
					for w in widgets_folder[widget['widget_class']]:
						if w['text'] == widget['text'] and w['content-desc'] == widget['content-desc'] and w['dimensions']['width'] == widget['dimensions']['width'] and w['dimensions']['height'] == widget['dimensions']['height']:
							duplicate = True
							break
					if not duplicate:
						widgets_folder[widget['widget_class']].append(widget)
						n2 = stats[widget['widget_class']]
						n2[1] += 1
						#stats.pop(widget['widget_class'], None)
						stats[widget['widget_class']] = n2



def getColor(rgb):
	hex = "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
	# color = Color(hex)
	return hex
	#return color.name



def getFragments(folder):
	fragments = {}
	for infile in glob.glob(folder + "/stoat_fsm_output/ui/*.xml"):
		with open(infile, 'r', encoding='utf-8') as f:
			tree = etree.parse(infile)
			for leaf in tree.xpath('//*[not(*)]'):
				if "Layout" in leaf.attrib["class"] and leaf.attrib["resource-id"] is not "":
					fragments[tree.getpath(leaf.getparent()) + "#" + leaf.attrib["resource-id"]] = infile

	return fragments


def checkFragments(inputFile_xml, fragments):
	tree = etree.parse(inputFile_xml)
	root = tree.getroot()
	identify_fragments = etree.XPath("//*[@resource-id=$var]")
	identify_leaf = etree.XPath(".//*[not(*)]")

	if fragments:
		for key in fragments:
			path_to_root = key.split("#")[0]
			rid = key.split("#")[1]
			for fragment in identify_fragments(root, var=rid):
				if tree.getpath(fragment.getparent()) == path_to_root and fragment.getchildren():
					return True
	else:
		return False


def compareHisto(first, sec):
	imA = Image.open(first)
	imB = Image.open(sec)

	# Normalise the scale of images
	if imA.size[0] > imB.size[0]:
		imA = imA.resize((imB.size[0], imA.size[1]))
	else:
		imB = imB.resize((imA.size[0], imB.size[1]))

	if imA.size[1] > imB.size[1]:
		imA = imA.resize((imA.size[0], imB.size[1]))
	else:
		imB = imB.resize((imB.size[0], imA.size[1]))

	hA = imA.histogram()
	hB = imB.histogram()
	sum_hA = 0.0
	sum_hB = 0.0
	diff = 0.0

	for i in range(len(hA)):
		#print(sum_hA)
		sum_hA += hA[i]
		sum_hB += hB[i]
		diff += abs(hA[i] - hB[i])

	return diff/(2*max(sum_hA, sum_hB))


def process(folder):
	global stats
	widgets_folder = {}
	for w in target_list:
		widgets_folder[w] = []

	folder_name = os.path.basename(folder)
	#print(folder_name)
	#fragments = getFragments(folder)
	# print("")
	# print(folder)
	# print 'process id:', os.getpid()
	for infile in sorted(sorted(glob.glob(folder + "/stoat_fsm_output/ui/*.xml"), reverse=True), key=len, reverse=True):
	#for infile in sorted(sorted(glob.glob(folder + "/ui/*.xml"), reverse=True), key=len, reverse=True):
		#print(infile)
		# print 'process id:', os.getpid()
		widgets_xml = []
		status_bar = False
		ads_banner = False
		ads_y1 = 0
		ads_y2 = 0
		name, ext = os.path.splitext(infile)
		pngfile = infile.replace(".xml", ".png")

		if os.path.exists(pngfile) and os.stat(pngfile).st_size > 0 and checkFileValidity(infile) and checkDuplicateFile(infile):
			#if checkFragments(infile, fragments):
			#	continue
			#with open(infile, 'r', encoding='utf-8') as f:
			#print infile
			#tree = etree.parse(infile)
			ctx = etree.iterparse(infile, events=('start',), tag='node')
			# iterparse first round to identify presence of status_bar, ads_banner
			for event, elem in ctx:
				# check for android status bar
				if elem.attrib['bounds'] == "[0,33][800,1216]":
					status_bar = True

				#check for advertisement banner
				if 'Ad' in elem.attrib['resource-id']:
					for child in elem.iterchildren():
						if child.attrib['class'] == "android.widget.ViewSwitcher":
							ads_banner = True
							c = re.findall(r"(?<=\[).*?(?=\])", child.attrib["bounds"])
							c_from = tuple(map(int, c[0].split(",")))
							c_to = tuple(map(int, c[1].split(",")))
							ads_y1 = c_from[1]
							ads_y2 = c_to[1]


			ctx = etree.iterparse(infile, events=('start',), tag='node')
			for event, elem in ctx:
				widget_name = elem.attrib['class'].split('.')[-1]
				#print(widget_name)
				coordinates = re.findall(r"(?<=\[).*?(?=\])", elem.attrib["bounds"])
				if len(coordinates) != 2:
					continue

				coor_from = tuple(map(int, coordinates[0].split(",")))
				coor_to = tuple(map(int, coordinates[1].split(",")))

				if widget_name == "View" and coor_from == (0,33) and coor_to == (800,1216):
					continue

				if status_bar and (coor_from[1] < 33 or coor_to[1] < 33):
					continue


				if ads_banner and ((coor_from[1] >= ads_y1 and coor_from[1] <= ads_y2) or (coor_to[1] >= ads_y1 and coor_to[1] <= ads_y2)) :
					continue

				if (coor_to[0] - coor_from[0] <= 1) or (coor_to[1] - coor_from[1] <= 1):
					continue

				if not (coor_from[0] > 800 or coor_from[0] < 0 or coor_to[0] > 800 or coor_to[0] < 0 or coor_from[1] > 1216 or coor_from[1] < 0 or coor_to[1] > 1216 or coor_to[1] < 0):
					#print "[+]" + elem.attrib['resource-id'], elem.attrib['class']
					#print("hi")
					meta_data = {}
					meta_data['widget_class'] = widget_name
					meta_data['coordinates'] = {'from': coor_from, 'to': coor_to}
					meta_data['leaf'] = False
					meta_data['rid'] = elem.attrib['resource-id']
					if len(elem.getchildren()) == 0: # identify leaf node
						meta_data['leaf'] = True
						meta_data['dimensions'] = getDimensions(coor_from, coor_to)
						if meta_data['dimensions']['width'] == 0 or meta_data['dimensions']['height'] == 0:
							continue

						#text = re.findall(r'(?<=text=\").*?(?=\")', line)
						meta_data['text'] = elem.attrib['text']
						meta_data['clickable'] = elem.attrib['clickable']
						meta_data['focusable'] = elem.attrib['focusable']
						#desc = re.findall(r'(?<=content-desc=\").*?(?=\")', line)
						meta_data["content-desc"] = elem.attrib['content-desc']
						#meta_data['XML'] = infile
						#meta_data['PNG'] = pngfile
						meta_data['src'] = name
						if widget_name in target_list:

							num = stats[widget_name]
							#print(num)
							#print("num:"+num)
							num[0] += 1
							#stats.pop(widget_name, None)
							stats[widget_name] = num

					widgets_xml.append(meta_data)
					#print(widgets_xml)
					#print(widgets_folder)

		remove_overlap_duplicates(widgets_xml, widgets_folder)

	return widgets_folder

def init(c, h, s):
	global count
	global hash_dict
	global stats
	count = c
	hash_dict = h
	stats = s
	for t in target_list:
		stats[t] = [0] * 2


if __name__ == '__main__':

	if os.path.exists(archive_dir):
		shutil.rmtree(archive_dir)
	os.makedirs(archive_dir)

	meta_dump = {}
	for w in target_list:
		meta_dump[w] = {}

	count = Value('i', 1)
	#print(type(count))
	hash_dict = Manager().dict()
	stats = Manager().dict()

	folders = glob.glob(a.input_dir + "/**")
	#folders = glob.glob(a.input_dir + "/*20170510_cleaned*/**")
	start_time = time.time()

	pool = Pool(processes=8, initializer=init, initargs=(count, hash_dict, stats,))

	num_processed = 0
	further_remove = {}
	for t in target_list:
		further_remove[t] = 0
	for w in pool.imap(process, folders):
		further_remove = createClippings(w, meta_dump, further_remove)
		num_processed += 1
		#print(num_processed)
		if num_processed%5 is 0:
			print "%s of %s processed" % (num_processed, len(folders))

	pool.close()
	pool.join()

	meta_dump_combined = {}
	for widget in meta_dump:
		#print("11111")
		#print(widget)
		for entry in meta_dump[widget]:
			#print(entry)
			meta_dump_combined[entry] = meta_dump[widget][entry]

	with open(os.path.join(archive_dir, "meta_dump.txt"), "a+") as f:
		#print(meta_dump_combined)
		json.dump(meta_dump_combined, f, sort_keys=True, indent=3, separators=(',', ': '))

	with open(os.path.join(archive_dir, "statistics.txt"), "a+") as f:
		temp = dict(stats)
		for k, v in temp.iteritems():
			temp[k] += (further_remove[k],)
			initial = 0.0
			further = 0.0
			if v[0] != 0:
				initial = float(v[0] - v[1]) / v[0]
				further = float(v[1] - v[2]) / v[0]
			print initial
			f.write(
			    "{} {} {:.2%} {:.2%}\n".format(
			        k,
			        v,
			        initial,
			        further
			        )
			    )


	'''
	for folder in os.listdir("./widget_clippings"):
		files = glob.glob("widget_clippings/" + folder + "/*.png")
		for f1, f2 in itertools.combinations(files, 2):
			try:
				if compareHisto(f1, f2) < 0.07:
					os.remove(f2)
			except Exception as e:
				continue
	'''


	'''
	for folder in os.listdir("./widget_clippings"):
		if folder == "meta_dump.txt":
			continue
		else:
			files = deque(glob.glob("widget_clippings/" + folder + "/*.png"))
			f1 = files[0]
			files.popleft()
			for f in files:
				if compareHisto(f1, f) < 0.97:
					os.remove(f)
	'''

	elapsed_time = time.time() - start_time
	print "[+]Elapsed time: " + str(elapsed_time)
