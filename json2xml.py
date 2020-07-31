import os
import json


def json2xml(json_path):
    with open(json_path, 'r', encoding='utf-8')as fp:
        json_data = json.load(fp)
        print(type(json_data))
        width = json_data['imageWidth']
        height = json_data['imageHeight']
        objects_list = json_data['shapes']
        print(type(objects_list))
        for ob in objects_list:
            # print(type(ob),ob)
            points = ob['points']
            label = ob['label']
            print(label)
