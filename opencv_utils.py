#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:HSV_demo.py
@ datetime:2020/8/4 17:08
@software: PyCharm

"""
import cv2
import numpy as np

def calcAndDrawHist(image, color):
    hist = cv2.calcHist([image], [0], None, [256], [0.0, 255.0])
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)
    histImg = np.zeros([256, 256, 3], np.uint8)
    hpt = int(0.9 * 256);

    for h in range(256):
        intensity = int(hist[h] * hpt / maxVal)
        cv2.line(histImg, (h, 256), (h, 256 - intensity), color)
    return histImg


def hsv_demo():
    """
    1、 设置感兴趣区域，中心区域
    2、 将感兴趣区域转为为hsv图像
    3、 对感兴趣区域进行H通道直方图投影，计算最高峰的H值，设maxh
    4、 在原图上找出[maxh-x,maxh+x]范围内区域
    5、 去除噪声，选取车厢区域的矩形边界
    cv2.bitwise_and 加运算
    """
    img_path = "D:/abner/project/jzx.jpg"
    img = cv2.imread(img_path)
    #hsv 图
    hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    cv2.imshow("hsv",hsv_img)

    # b, g, r = cv2.split(img)
    # histImgB = calcAndDrawHist(b, [255, 0, 0])
    # histImgG = calcAndDrawHist(g, [0, 255, 0])
    # histImgR = calcAndDrawHist(r, [0, 0, 255])
    # h 通道直方图
    img_h = hsv_img[..., 0]
    img_h_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_h_hist = calcAndDrawHist(img_h_gray, [255, 0, 0])
    #直方图的最高值
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(img_h)
    # img_h = np.asarray(img_h)
    lower = maxVal-100
    upper= maxVal+100
    #获得在特定值范围内的区域
    mask = cv2.inRange(img_h, lower, upper)
    # 高斯滤波
    sinkblur = cv2.GaussianBlur(mask, (5, 5), 0)
    print(maxVal,minVal)
    #threshold(src, thresh, maxval, type, dst=None)
    # 选择特定值区域cv2.THRESH_BINARY cv2.THRESH_TOZERO_INV 二值化255
    rec,thresh1 = cv2.threshold(img,50,255,cv2.THRESH_BINARY)
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # rec2, thresh2 = cv2.threshold(gray, maxVal - 1, maxVal + 1, cv2.THRESH_BINARY)


    #搜索轮廓
    # frame = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    frame = cv2.GaussianBlur(mask, (5, 5), 0)

    img2 = img.copy()
    rec2, thresh2 = cv2.threshold(frame, 50, 255, cv2.THRESH_BINARY)
    src_img = find_contours(img,thresh2)

    # 填充掉
    # cv2.fillConvexPoly(img2, contours[max_idx], 0)

    cv2.imshow("img_h", img_h_hist)
    cv2.imshow("img_h_val", thresh1)
    cv2.imshow("mask", mask)
    cv2.imshow("histImgG", frame)
    cv2.imshow("histImgR", img)
    cv2.imshow("img2", img2)
    cv2.imshow("img_", src_img)
    cv2.waitKey(0)

def find_contours(src_img,gray_img):
    """
    给出原图和灰度图查找连通域
    cv2.findContours() 函数进行查找
    cv2.boundingRect获得坐标
    cv2.contourArea()获取面积
    """
    # 过滤小于阈值的连通域
    threshold_area = 60
    # 查找连通域 必须是灰度图
    image,contours, hierarchy = cv2.findContours(gray_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 把所有的连通域显示出来
    # cv2.drawContours(src_img, contours, -1, (0, 255, 255), 2)
    # 查找最大连通域
    area = []
    max_area = 0
    # 遍历所有的连通域
    for i in range(0, len(contours)):

        cnt = contours[i]

        # 获得坐标框
        x, y, w, h = cv2.boundingRect(cnt)
        temp_are = (w)*(h)
        if temp_are > max_area:
            max_area = temp_are
            print(max_area,x,y,w,h)
            ob_x,ob_y,ob_w,ob_h = x, y, w, h

        # 获取面积
        ob_area = cv2.contourArea(cnt)
        # print(i, x, y, w, h,ob_area)
        # 面积大于1000才显示
        if ob_area > threshold_area:
            print("ob_area ", ob_area)
            cv2.rectangle(src_img, (x, y), (x + w, y + h), (0, 0, 255), 4)
        area.append(cv2.contourArea(contours[i]))
        # if ob_area > max_area:
        #     # max_area = ob_area
        #     print("index ",i,max_area)
    #最大面积索引
    max_idx = np.argmax(area)
    cv2.rectangle(src_img, (ob_x, ob_y), (ob_x + ob_w, ob_y + ob_h), (0, 0, 255), 4)
    return src_img
def idcard_region():

    idcard_img = "D:/abner/project/dataset/idcard/VOC2007/JPEGImages/20.jpg"
    img = cv2.imread(idcard_img)
    #resize
    img = cv2.resize(img,(600,449))
    #灰度图
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #H 通道
    img_h = hsv_img[..., 0]

    img_h_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_h_hist = calcAndDrawHist(img_h_gray, [255, 0, 0])
    #高斯滤波
    img_h_gray = cv2.GaussianBlur(img_h_gray, (3, 3), 0)

    #图像最大值和最小值
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(img_h_gray)

    #二值化
    # rec2, thresh2 = cv2.threshold(img_h_gray, 10, 255, cv2.THRESH_BINARY)
    # print("val th1 ", rec2)
    #大律法otsu
    rec2,thresh2 = cv2.threshold(img_h_gray,50,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    print("val th ",rec2)
    #自适应阈值
    # adp_thresh = cv2.adaptiveThreshold(img_h_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
    #                            cv2.THRESH_BINARY, 11, 2)
    # 高斯滤波
    # adp_thresh2 = cv2.GaussianBlur(adp_thresh, (3, 3), 0)
    # 反色，即对二值图每个像素取反
    result = cv2.bitwise_not(thresh2)
    cv2.imshow("thresh2 ", result)
    # gauss_img  = cv2.GaussianBlur(result, (3, 3), 0)
    # cv2.imshow("gauss img ",gauss_img)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    eroded = cv2.erode(result, kernel)  # 腐蚀图像
    dilated = cv2.dilate(eroded, kernel)  # 膨胀图像

    # cv2.imshow("erode",eroded)



    # X Gradient
    xgrad = cv2.Sobel( img_h_gray, cv2.CV_16SC1, 1, 0)  # 计算梯度，（API要求不能为浮点数）
    # Y Gradient
    ygrad = cv2.Sobel( img_h_gray, cv2.CV_16SC1, 0, 1)
    # grad_x = cv2.Scharr(img_h_gray, cv2.CV_16SC1, 1, 0)
    # grad_y = cv2.Scharr(img_h_gray, cv2.CV_16SC1, 0, 1)
    # edge 边缘检测
    #像素值最大值和最小值当做高低阈值
    threshold_val = (maxVal + minVal) / 2
    threshold_low = maxVal*0.5
    #有两种方式，一种是canny(img,thresh1,thresh2),另一种是通过梯度cany(xgrad,ygrad,thresh1,thresh2)
    edge_output = cv2.Canny(xgrad,ygrad,  threshold_val, threshold_low)  # 调用cv.Canny，利用高低阈值求出图像边缘
    cv2.imshow("edge ",edge_output)
    #中值滤波
    img_medianBlur = cv2.medianBlur(edge_output, 3)  # 中值滤波
    cv2.imshow("midd result", img_medianBlur)  # 显示中值滤波结果
    gauss_img = cv2.GaussianBlur(edge_output, (5, 5), 0)
    cv2.imshow("gauss img ", gauss_img)

    #边缘提取后进行腐蚀


    eroded_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    eroded = cv2.erode(gauss_img.copy(), eroded_kernel)  # 腐蚀图像
    cv2.imshow("eroded ", eroded)

    dilated_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(img_medianBlur, dilated_kernel)  # 膨胀图像
    cv2.imshow("dilated ",dilated)

    # 闭运算
    kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    closing_img = cv2.morphologyEx(dilated.copy(),cv2.MORPH_CLOSE,kernel3)
    cv2.imshow("closing ",closing_img)
    #开运算
    kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # open_img = cv2.morphologyEx(closing_img.copy(), cv2.MORPH_OPEN, kernel2)
    # cv2.imshow("opening ", open_img)

    src_img = find_contours(img, closing_img )
    cv2.imshow("count ",src_img)

    cv2.waitKey(0)
def cut_region():
    idcard_img = "D:/abner/project/dataset/idcard/VOC2007/JPEGImages/1.jpg"

    img = cv2.imread(idcard_img)
    # resize
    img = cv2.resize(img, (600, 449))
    # 灰度图
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow('img gray ',img_gray)

    # X Gradient
    xgrad = cv2.Sobel(img_gray, cv2.CV_16SC1, 1, 0)  # 计算梯度，（API要求不能为浮点数）
    # Y Gradient
    ygrad = cv2.Sobel(img_gray, cv2.CV_16SC1, 0, 1)

    # 图像最大值和最小值
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(img_gray)
    print("max loc ",maxLoc)
    # edge 边缘检测
    # 像素值最大值和最小值当做高低阈值
    threshold_val = (maxVal + minVal) / 2
    threshold_low = maxVal * 0.5
    # 有两种方式，一种是canny(img,thresh1,thresh2),另一种是通过梯度cany(xgrad,ygrad,thresh1,thresh2)
    edge_output = cv2.Canny(xgrad, ygrad, threshold_val, threshold_low)  # 调用cv.Canny，利用高低阈值求出图像边缘
    cv2.imshow("edge ", edge_output)

    con_img = find_contours(img,edge_output)
    cv2.imshow("con ",con_img)

    cv2.waitKey(0)
    cv2.destroyWindow()

def dete_line():
    idcard_img = "D:/abner/project/dataset/idcard/VOC2007/JPEGImages/1.jpg"

    img = cv2.imread(idcard_img)
    # resize
    img = cv2.resize(img, (600, 449))
    # 灰度图
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow('img gray ',img_gray)

    # X Gradient
    xgrad = cv2.Sobel(img_gray, cv2.CV_16SC1, 1, 0)  # 计算梯度，（API要求不能为浮点数）
    # Y Gradient
    ygrad = cv2.Sobel(img_gray, cv2.CV_16SC1, 0, 1)

    # 图像最大值和最小值
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(img_gray)
    print("max loc ",maxLoc)
    # edge 边缘检测
    # 像素值最大值和最小值当做高低阈值
    threshold_val = (maxVal + minVal) / 2
    threshold_low = maxVal * 0.5
    # 有两种方式，一种是canny(img,thresh1,thresh2),另一种是通过梯度cany(xgrad,ygrad,thresh1,thresh2)
    edge_output = cv2.Canny(xgrad, ygrad, threshold_val, threshold_low)  # 调用cv.Canny，利用高低阈值求出图像边缘
    cv2.imshow("edge ", edge_output)

    lines = cv2.HoughLines(edge_output, 1, np.pi / 180, 118)
    result = img.copy()
    for line in lines:
        rho = line[0][0]  # 第一个元素是距离rho
        theta = line[0][1]  # 第二个元素是角度theta
        print(rho)
        print(theta)
        if (theta < (np.pi / 4.)) or (theta > (3. * np.pi / 4.0)):  # 垂直直线
            pt1 = (int(rho / np.cos(theta)), 0)  # 该直线与第一行的交点
            # 该直线与最后一行的焦点
            pt2 = (int((rho - result.shape[0] * np.sin(theta)) / np.cos(theta)), result.shape[0])
            cv2.line(result, pt1, pt2, (255))  # 绘制一条白线
        else:  # 水平直线
            pt1 = (0, int(rho / np.sin(theta)))  # 该直线与第一列的交点
            # 该直线与最后一列的交点
            pt2 = (result.shape[1], int((rho - result.shape[1] * np.cos(theta)) / np.sin(theta)))
            cv2.line(result, pt1, pt2, (255), 1)

    cv2.imshow('result', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def sift_region():

    template_img_path = "D:/abner/project/dataset/idcard/VOC2007/JPEGImages/1.jpg"
    com_img_path = "D:/abner/project/dataset/idcard/VOC2007/JPEGImages/3.jpg"

    template_img = cv2.imread(template_img_path)
    com_img = cv2.imread(com_img_path)

    sift = cv2.xfeatures2d.SIFT_create()
    #灰度图
    template_img_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
    com_img_gray = cv2.cvtColor(com_img, cv2.COLOR_BGR2GRAY)

    kp1, des1 = sift.detectAndCompute(template_img_gray, None)  # des是描述子
    kp2, des2 = sift.detectAndCompute(com_img_gray, None)  # des是描述子

    points2f = cv2.KeyPoint_convert(kp1)  # 将KeyPoint格式数据中的xy坐标提取出来。
    print(kp1)
    print(points2f)
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2,k=2)

    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])

    img5 = cv2.drawMatchesKnn(template_img, kp1, com_img, kp2, good, None, flags=2)

    cv2.imshow("img_h3", img5)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # hsv_demo()
    # idcard_region()
    # cut_region()
    # sift_region()
    dete_line()
