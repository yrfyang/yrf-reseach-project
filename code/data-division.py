import json
import os
import random

archive_dir = 'data_set'
file1 = 'widget_clippings/meta_dump.txt'
if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)
with open(file1) as f:
    content = f.read()
    j_dict = json.loads(content)
    image_data = dict()
    m = 0
    for key, value in j_dict.items():
        src = value['src']
        if src not in image_data.keys():
            image_data[src] = list()
        if value['hog_fd_average'] >= 0 and value['hog_fd_var'] >= 0 and value['hog_image_average'] >= 0 and value['hog_image_var'] >= 0:
            hog_list = list()
            hog_list.append(value['hog_fd_average'])
            hog_list.append(value['hog_fd_var'])
            hog_list.append(value['hog_image_average'])
            hog_list.append(value['hog_image_var'])
            image_data[src].append(hog_list)
    for key, value in image_data.items():
        if len(value) >= 3:
            m = m + 1
            hog_fd_average = 0
            hog_fd_var = 0
            hog_image_average = 0
            hog_image_var = 0
            for item in value:
                hog_fd_average += item[0]
                hog_fd_var += item[1]
                hog_image_average += item[2]
                hog_image_var += item[3]
            hog_fd_average = hog_fd_average / len(value)
            hog_fd_var = hog_fd_average / len(value)
            hog_image_average = hog_fd_average / len(value)
            hog_image_var = hog_fd_average / len(value)
            data = ""
            try:
                with open(archive_dir +  'data.txt', 'r') as f1:
                    for line in f1:
                        data += line
            except:
                pass
            with open(archive_dir +  'data.txt', 'w') as f1:
                f1.write(data)
                f1.write("+1")
                f1.write(" 1:"+ str(hog_fd_average))
                f1.write(" 2:"+ str(hog_fd_var))
                f1.write(" 3:"+ str(hog_image_average))
                f1.write(" 4:"+ str(hog_image_var))
                f1.write("\n")
    key_list = image_data.keys()
    n = 0
    while n < m:
        n = n + 1
        s = []
        num_of_component = random.randint(3, 7)
        while(len(s) < num_of_component):
            x = random.randint(0, len(key_list) - 1)
            if x not in s and len(image_data[key_list[x]]) != 0:
                s.append(x)
        for i in s:
            list1 = image_data[key_list[i]]
            a = random.randint(0, len(list1) - 1)
            hog_fd_average = hog_fd_average + list1[a][0]
            hog_fd_var = hog_fd_var + list1[a][1]
            hog_image_average = hog_image_average + list1[a][2]
            hog_image_var = hog_image_var + list1[a][3]
        hog_fd_average = hog_fd_average / len(s)
        hog_fd_var = hog_fd_var / len(s)
        hog_image_average = hog_image_average / len(s)
        hog_image_var = hog_image_var / len(s)
        data = ""
        try:
            with open(archive_dir +  'data.txt', 'r') as f1:
                for line in f1:
                    data += line
        except:
            pass
        with open(archive_dir +  'data.txt', 'w') as f1:
            f1.write(data)
            f1.write("-1")
            f1.write(" 1:"+ str(hog_fd_average))
            f1.write(" 2:"+ str(hog_fd_var))
            f1.write(" 3:"+ str(hog_image_average))
            f1.write(" 4:"+ str(hog_image_var))
            f1.write("\n")
