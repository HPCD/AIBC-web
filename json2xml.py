import os
import json
from xmljson import parker
import cv2

from abner_train_src.myexample.create_annatation_xml import CreateAnnatationXml
json_path = "D:/abner/project/dataset/idcard/json/1.json"


def json2xml(json_path):
    with open(json_path, 'r', encoding='utf-8')as fp:
        json_data = json.load(fp)
        print(json_data)
        root = "D:/abner/project/dataset/idcard/"
        img_path = root+json_data['imagePath'].replace("..\\","")
        img = cv2.imread(img_path)
        print(img_path)
        width = json_data['imageWidth']
        height = json_data['imageHeight']
        cre_xml = CreateAnnatationXml(width,height)
        objects_list = json_data['shapes']
        print(type(objects_list))
        for ob in objects_list:
            # print(type(ob),ob)
            points = ob['points']
            xmin = points[0][0]
            ymin = points[0][1]
            xmax = points[1][0]
            ymax = points[1][1]
            label = ob['label']
            cre_xml.set_object(label,xmin,ymin,xmax,ymax)
            cv2.rectangle(img, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (125, 255, 51), thickness=4)
        # xml_path = json_path.repalec('.json','.xml')
        # cre_xml.save_xml_file(xml_path)
        # print(label)

    # creatAXml.save_xml_file(img_path.replace(".jpg",".xml"))
    cv2.namedWindow("test", 0);
    cv2.resizeWindow("test", 640, 480)
    cv2.imshow("test", img)
    cv2.waitKey(0)


if __name__ == "__main__":
    json2xml(json_path)
