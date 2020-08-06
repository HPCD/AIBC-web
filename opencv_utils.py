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
