import json
import os
import random
import numpy as np

def overlap(s, x, image_data, key_list):
    listb = image_data[key_list[x]]
    ol_flag = True
    out = list()
    for item in listb:
        out.append(item)
        flag = 1
        from_x = item[4]
        to_x = item[5]
        from_y = item[6]
        to_y = item[7]
        for i in s:
            lista = image_data[key_list[i]]
            ol_flag1 = True
            for item1 in lista:
                if not(((item1[4] < to_x and item1[4] >= from_x) or (item1[5] <= to_x and item1[5] > from_x)) and ((item1[6] < to_y and item1[6] >= from_y) or (item1[7] <= to_y and item1[7] > from_y))):
                    out.append(item1)
                    ol_flag1 = False
                    break
            if ol_flag1 == True:
                if len(out) > 1:
                    for n in range(len(out) - 1, 0, -1):
                        del out[n]
                flag = 0
                break
        if flag == 1:
            ol_flag = False
            break
        else:
            del out[0]
    return out


archive_dir = 'data_set'
file1 = 'widget_clippings/meta_dump.txt'
x_length = 800 / 6
y_length = 1216 / 8
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
            hog_list.append(value['coordinates']['from'][0])
            hog_list.append(value['coordinates']['from'][1])
            hog_list.append(value['coordinates']['to'][0])
            hog_list.append(value['coordinates']['to'][1])
            image_data[src].append(hog_list)
    for key, value in image_data.items():
        if len(value) >= 3:
            m = m + 1
            hog_fd_average = 0
            hog_fd_var = 0
            hog_image_average = 0
            hog_image_var = 0
            position = np.zeros((8,6))
            for item in value:
                if item[4] >= 798:
                    item[4] = 797
                from_x = item[4] / x_length
                if item[6] >= 798:
                    item[6] = 797
                to_x = item[6] / x_length
                if item[5] == 1216:
                    item[5] = item[5] - 1
                from_y = item[5] / y_length
                if item[7] == 1216:
                    item[7] = item[7] - 1
                to_y = item[7] / y_length
                for i in range(from_x, to_x + 1):
                    for j in range(from_y, to_y + 1):
                        position[j][i] = 1
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
                output_n  = 5
                for p in range(0, 8):
                    for q in range(0, 6):
                        f1.write(" " + str(output_n) + ":"+ str(position[p][q]))
                        output_n = output_n + 1
                f1.write("\n")
    key_list = image_data.keys()
    n = 0
    while n < m:
        n = n + 1
        s = []
        num_of_component = random.randint(3, 7)
        result = list()
        while(len(s) < num_of_component):
            x = random.randint(0, len(key_list) - 1)
            if x not in s and len(image_data[key_list[x]]) != 0 and len(overlap(s, x, image_data, key_list)) != 0:
                if len(s) == num_of_component - 1:
                    result = overlap(s, x, image_data, key_list)
                s.append(x)
        hog_fd_average = 0
        hog_fd_var = 0
        hog_image_average = 0
        hog_image_var = 0
        position = np.zeros((8,6))
        for item in result:
            hog_fd_average = hog_fd_average + item[0]
            hog_fd_var = hog_fd_var + item[1]
            hog_image_average = hog_image_average + item[2]
            hog_image_var = hog_image_var + item[3]
            if item[4] >= 798:
                item[4] = 797
            from_x = item[4] / x_length
            if item[6] >= 798:
                item[6] = 797
            to_x = item[6] / x_length
            if item[5] == 1216:
                item[5] = item[5] - 1
            from_y = item[5] / y_length
            if item[7] == 1216:
                item[7] = item[7] - 1
            to_y = item[7] / y_length
            for i in range(from_x, to_x + 1):
                for j in range(from_y, to_y + 1):
                    position[j][i] = 1
        hog_fd_average = hog_fd_average / len(result)
        hog_fd_var = hog_fd_var / len(result)
        hog_image_average = hog_image_average / len(result)
        hog_image_var = hog_image_var / len(result)
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
            output_n  = 5
            for p in range(0, 8):
                for q in range(0, 6):
                    f1.write(" " + str(output_n) + ":"+ str(position[p][q]))
                    output_n = output_n + 1
            f1.write("\n")
