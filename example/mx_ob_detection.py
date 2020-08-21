#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:mx_objection.py
@ datetime:2020/8/20 10:02
@software: PyCharm

"""
from gluoncv import model_zoo, data, utils
from matplotlib import pyplot as plt
import cv2
#yolo3_mobilenet0.25_coco yolo3_darknet53_voc, 只有设置pretrained_base=False 才不会从网上下载
net = model_zoo.get_model('yolo3_mobilenet1.0_coco', pretrained=False, pretrained_base=False)
#加载本地模型
net.load_parameters("D:/MyData/zhongbei/.mxnet/models/temp/yolo3_mobilenet1.0_coco-66dbbae6.params")
# net = model_zoo.get_model('ssd_512_mobilenet1.0_coco',pretrained=True)
im_fname = utils.download('https://raw.githubusercontent.com/zhreshold/' +
                          'mxnet-ssd/master/data/demo/dog.jpg',
                          path='dog.jpg')

im_fname = '2.jpg'
x, img = data.transforms.presets.yolo.load_test(im_fname, short=512)
print('Shape of pre-processed image:', x.shape)
class_IDs, scores, bounding_boxs = net(x)

ax = utils.viz.plot_bbox(img, bounding_boxs[0], scores[0],
                         class_IDs[0], class_names=net.classes)
# print(bounding_boxs,len(class_IDs),net.classes)
# class_IDs = class_IDs.asnumpy()

bboxes = bounding_boxs[0].asnumpy()
thresh = 0.5
scores = scores[0].asnumpy()
height = img.shape[0]
width = img.shape[1]
# bboxes[:, (0, 2)] *= width
# bboxes[:, (1, 3)] *= height
class_IDs = class_IDs[0].asnumpy()
# img = cv2.imread(im_fname)
for i, bbox in enumerate(bboxes):
    if scores is not None and scores.flat[i] < thresh:
        continue
    #只截取car
    if net.classes[int(class_IDs[i])] == 'car':
        xmin, ymin, xmax, ymax = [int(x) for x in bbox]
        print(xmin, ymin, xmax, ymax)
        cv2.imshow("df",img)

        img=img[ymin+5:ymax-5,xmin+5:xmax-5]
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # cv2.imshow("d",img)
        cv2.imwrite('d4.jpg',img)
        # cv2.waitKey(0)
    else:
        continue


# plt.show()
