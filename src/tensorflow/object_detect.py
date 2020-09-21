import numpy as np
import tensorflow as tf
"""
tensorflow object detection 模型进行目标检测推理代码
"""

tf.compat.v1.enable_eager_execution()
class TFDetectRegion():
    def __init__(self):
        """
        初始化模型
        root:模型所在根目录

        """

        self.root = "D:/abner/project/pyproject/object_detection/"

        self.model_dir = os.path.join(self.root , "abner_train_src/QAOCR/output/saved_model")
        self.model = tf.compat.v2.saved_model.load(str(self.model_dir), None)
        self.detection_model = self.model.signatures['serving_default']

        self.category_index =  {1: {'id': 1, 'name': 'person'}}

    def run_inference_for_single_image(self, image):
        image = np.asarray(image)
        # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
        input_tensor = tf.convert_to_tensor(image)
        # The model expects a batch of images, so add an axis with `tf.newaxis`.
        input_tensor = input_tensor[tf.newaxis, ...]
        # import numpy as np
        # import uuid
        # name = uuid.uuid4()
        # np.ndarray.tofile(input_tensor.numpy(),open(str(name)+"tensor.raw",'w'))
        # print(name)
        # Run inference
        output_dict = self.detection_model(input_tensor)

        # All outputs are batches tensors.
        # Convert to numpy arrays, and take index [0] to remove the batch dimension.
        # We're only interested in the first num_detections.
        # print("dfjdniigigg", output_dict.pop('num_detections'))
        num_detections = int(output_dict.pop('num_detections'))
        # num_detections = 3
        output_dict = {key: value[0, :num_detections].numpy()
                       for key, value in output_dict.items()}
        output_dict['num_detections'] = num_detections

        # detection_classes should be ints.
        output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

       
        boxes = output_dict['detection_boxes'],
        classes = output_dict['detection_classes'],
        scores = output_dict['detection_scores'],
        return classes,scores,boxes

    def get_img_region(self, img_path):
        """
        获取图片的检测区域
        """
        img = Image.open(img_path)


        width, height = img.size
        image_np = np.array(img)

        class_IDs, scores, bounding_boxs = self.run_inference_for_single_image(image_np)
        print(type(class_IDs),"s",type(scores),"d",type(bounding_boxs))

        bboxes = bounding_boxs[0]
        # 阈值
        thresh = 0.5
        scores = scores[0]
      
        class_IDs = class_IDs
       
        for i, bbox in enumerate(bboxes):
            if scores is not None and scores[i] < thresh:
                continue
            #顺序和mxnet有区别
            ymin, xmin, ymax, xmax = [float(x) for x in bbox]

            xmin = int(xmin*width)
            xmax = int(xmax*width)
            ymin = int(ymin*height)
            ymax = int(ymax*height)

            print("before ", xmin, ymin, xmax, ymax)
            # 对截图图片进行扩充
            # xmin, ymin, xmax, ymax = self.padding(xmin, ymin, xmax, ymax, width, height)

            img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

            result_img = img[ymin:ymax, xmin:xmax]
            print( xmin, ymin, xmax, ymax)
            # result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)

            img_root = "D:/abner/project/pyproject/chineseocr_lite-master/debug_im/"

            new_name = os.path.join(img_root, str(uuid.uuid1()) + ".jpg")
            cv2.imwrite(new_name, result_img)
            # cv2.imshow("cut ",result_img)
            # cv2.waitKey(1000)
            yield new_name

    def padding(self, xmin, ymin, xmax, ymax, org_w, org_h, padding=0.05):

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

        return int(xmin), int(ymin), int(xmax), int(ymax)
