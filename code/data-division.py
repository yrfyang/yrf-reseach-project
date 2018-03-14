import json
import os

archive_dir = 'data_set'
file1 = 'widget_clippings/meta_dump.txt'
if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)
if not os.path.exists(archive_dir+'/positive'):
    os.makedirs(archive_dir+'/positive')
if not os.path.exists(archive_dir+'/negative'):
    os.makedirs(archive_dir+'/negative')
with open(file1) as f:
    content = f.read()
    j_dict = json.loads(content)
    negative_data = dict()
    positive_data = dict()
    for key, value in j_dict.items():
        app_name = value['src'].split('/')[-4]
        if app_name not in negative_data.keys():
            negative_data[app_name] = list()
        negative_data[app_name].append(key)
    n = 0
    print(negative_data)
    while n < 5000:
        if os.path.exists(archive_dir + '/negative/' + str(n) + '.txt'):
            os.remove(archive_dir + '/negative/' + str(n) + '.txt')
        key_list = negative_data.keys()
        output = list()
        for i in range(len(key_list)):
            value_i_list = key_list[i]
            negative_data[value_i_list]
            for o in range(len(negative_data[value_i_list])):
                output.append(negative_data[value_i_list][o])
                for j in range(i + 1,len(key_list)):
                    value_j_list = key_list[j]
                    for p in range(len(negative_data[value_j_list])):
                        output.append(negative_data[value_j_list][p])
                        for k in range(j + 1, len(key_list)):
                            value_k_list = key_list[k]
                            for q in range(len(negative_data[value_k_list])):
                                output.append(negative_data[value_k_list][q])
                                with open(archive_dir + '/negative/' + str(n) + '.txt', 'w') as f1:
                                    for item in output:
                                        f1.write(item + '\n')
        n = n + 1
    m = 0
    for key, value in j_dict.items():
        src = value['src']
        if src not in positive_data.keys():
            positive_data[src] = list()
        positive_data[src].append(key)
    for key, value in positive_data.items():
        if len(value) >= 3:
            m = m + 1
            key_list = key.split('/')
            new_key = key_list[-1] + '\\' + key_list[-4]
            if os.path.exists(archive_dir + '/positive/' + new_key + '.txt'):
                os.remove(archive_dir + '/positive/' + new_key + '.txt')
            #     os.makedirs(archive_dir + '/positive/' + new_key + '.txt')
            with open(archive_dir + '/positive/' + new_key + '.txt', 'w') as f1:
                for item in value:
                    f1.write(item + '\n')
    print(m)
