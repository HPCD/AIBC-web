import os
import json
import time
import web
import numpy as np
import uuid
from PIL import Image,ImageEnhance
import cv2
from model import  text_predict,crnn_handle
from mxnet import gluon
import gluoncv as gcv
import mxnet as mx
"""
mxnet 目标检测推理代码
"""
class MXDetectRegion():
    def __init__(self):
        """
        初始化模型
        root:模型所在根目录

        """

        self.root = "D:/abner/project/pyproject/canvas/src/sava_params/"
        self.symbol_json = self.root + 'ssd_resnet34_914-symbol.json'
        self.params_file = self.root + 'ssd_resnet34_914-0000.params'
        self.net = gluon.SymbolBlock.imports(symbol_file=self.symbol_json,
                                        input_names=['data'], ctx=mx.cpu())
        # net = gcv.model_zoo.get_model('ssd_512_mobilenet1.0_custom',root=root, classes=classes, pretrained_base=False)
        self.net.load_parameters(self.params_file)

    def get_img_region(self,img_path):
        """
        获取图片的检测区域
        """
        x, img = gcv.data.transforms.presets.ssd.load_test(img_path, 512)
        class_IDs, scores, bounding_boxs = self.net(x)

        bboxes = bounding_boxs[0].asnumpy()
        # 阈值
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

            xmin, ymin, xmax, ymax = [int(x) for x in bbox]
            # 对截图图片进行扩充
            xmin, ymin, xmax, ymax = padding(xmin, ymin, xmax, ymax, width, height)

            result_img = img[ymin:ymax, xmin:xmax]
            result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)

            img_root = "D:/abner/project/pyproject/chineseocr_lite-master/debug_im/"

            new_name = os.path.join(img_root, str(uuid.uuid1()) + ".jpg")
            cv2.imwrite(new_name, result_img)
            # cv2.imshow("cut ",result_img)
            # cv2.waitKey(1000)
            yield new_name
    def padding(self,xmin, ymin, xmax, ymax,org_w,org_h,padding=0.05):

        w = xmax - xmin
        h = ymax - ymin

        dX = int(w * padding)  # 0.05为padding
        dY = int(h * padding)

        # apply padding to each side of the bounding box, respectively
        x = max(0, xmin - dX)
        y = max(0, ymin - dY)
        w = min(org_w, w + (dX * 2))
        h = min(org_h, h + (dY * 2))
        xmax = x + w
        ymax = y + h

        return xmin, ymin, xmax, ymax
