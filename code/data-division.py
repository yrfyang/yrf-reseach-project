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
    #negative_data = dict()
    image_data = dict()
    # for key, value in j_dict.items():
    #     app_name = value['src'].split('/')[-4]
    #     if app_name not in negative_data.keys():
    #         negative_data[app_name] = list()
    #     negative_data[app_name].append(key)
    # n = 0
    # print(negative_data)
    # while n < 5000:
    #     if os.path.exists(archive_dir + '/negative/' + str(n) + '.txt'):
    #         os.remove(archive_dir + '/negative/' + str(n) + '.txt')
    #     key_list = negative_data.keys()
    #     output = list()
    #     for i in range(len(key_list)):
    #         value_i_list = key_list[i]
    #         #negative_data[value_i_list]
    #         for o in range(len(negative_data[value_i_list])):
    #             output.append(negative_data[value_i_list][o])
    #             for j in range(i + 1,len(key_list)):
    #                 value_j_list = key_list[j]
    #                 for p in range(len(negative_data[value_j_list])):
    #                     output.append(negative_data[value_j_list][p])
    #                     for k in range(j + 1, len(key_list)):
    #                         value_k_list = key_list[k]
    #                         for q in range(len(negative_data[value_k_list])):
    #                             output.append(negative_data[value_k_list][q])
    #                             with open(archive_dir + '/negative/' + str(n) + '.txt', 'w') as f1:
    #                                 for item in output:
    #                                     f1.write(item + '\n')
    #     n = n + 1
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
            # key_list = key.split('/')
            # new_key = key_list[-1] + '\\' + key_list[-4]
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
            print(hog_fd_average)
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

    print(m)
    key_list = image_data.keys()
    n = 0
    while n < m:
        n = n + 1
        s = []
        while(len(s) < 3):
            x = random.randint(0, len(key_list) - 1)
            if x not in s and len(image_data[key_list[x]]) != 0:
                s.append(x)
        list1 = image_data[key_list[s[0]]]
        list2 = image_data[key_list[s[1]]]
        list3 = image_data[key_list[s[2]]]
        print("<<<<<<<<")
        print(list1)
        print(list2)
        print(list3)
        a = random.randint(0, len(list1) - 1)
        b = random.randint(0, len(list2) - 1)
        c = random.randint(0, len(list3) - 1)
        hog_fd_average = (list1[a][0] + list2[b][0] + list3[c][0]) / 3
        hog_fd_var = (list1[a][1] + list2[b][1] + list3[c][1]) / 3
        hog_image_average = (list1[a][2] + list2[b][2] + list3[c][2]) / 3
        hog_image_var = (list1[a][3] + list2[b][3] + list3[c][3]) / 3
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
