
import time
from matplotlib import pyplot as plt
import numpy as np
import mxnet as mx
from mxnet import autograd, gluon
import gluoncv as gcv
from gluoncv.utils import download, viz
from gluoncv.utils.metrics.voc_detection import VOC07MApMetric
from src.vocdataset import VOCLike

from gluoncv.data.batchify import Tuple, Stack, Pad
from gluoncv.data.transforms.presets.ssd import SSDDefaultTrainTransform, SSDDefaultValTransform
"""
通过finetune的方式训练ssd 模型
"""


class MXTrainOb():
    def __init__(self, dataset_root='D:/abner/project/dataset/idcard/'):
        # 修改成自己数据的标签名
        self.classes = ['one']
        self.finetune_model_name = 'ssd_512_resnet50_v1_voc'
        self.finetune_model_save_dir = './model'
        self.export_model_file = "D:/abner/project/pyproject/canvas/src/sava_params/ssd_resnet34_921_ocr"
        #数据集
        self.dataset_root = dataset_root
        self.train_dataset = VOCLike(root=dataset_root, splits=((2007, 'train'),))
        self.val_dataset = VOCLike(root=dataset_root, splits=((2007, 'test'),))
        self.val_metric = VOC07MApMetric(iou_thresh=0.5, class_names=self.classes)
        self.num_workers = 0

        #模型加载
        self.net = gcv.model_zoo.get_model(self.finetune_model_name, pretrained=True, root=self.finetune_model_save_dir)
        #重置训练标签
        self.net.reset_class(self.classes)

        try:
            a = mx.nd.zeros((1,), ctx=mx.gpu(0))
            self.ctx = [mx.gpu(0)]
        except:
            self.ctx = [mx.cpu()]
        # self.ctx = [mx.cpu()]
        # print(self.ctx)
        #############################################################################################
        # Start training(finetuning)
        self.net.collect_params().reset_ctx(self.ctx)
        self.trainer = gluon.Trainer(
            self.net.collect_params(), 'sgd',
            {'learning_rate': 0.001, 'wd': 0.0005, 'momentum': 0.9})

        self.mbox_loss = gcv.loss.SSDMultiBoxLoss()
        self.ce_metric = mx.metric.Loss('CrossEntropy')
        self.smoothl1_metric = mx.metric.Loss('SmoothL1')
        self.best_map = [0]

        self.train_data, self.val_data = self.get_dataloader(self.train_dataset, self.val_dataset, 512, 9)

    def get_dataloader(self, train_dataset, val_dataset, data_shape, batch_size):
        """Get dataloader."""
        width, height = data_shape, data_shape
        # use fake data to generate fixed anchors for target generation
        with autograd.train_mode():
            _, _, anchors = self.net(mx.nd.zeros((1, 3, height, width), self.ctx[0]))
        anchors = anchors.as_in_context(mx.cpu())
        batchify_fn = Tuple(Stack(), Stack(), Stack())  # stack image, cls_targets, box_targets
        train_loader = gluon.data.DataLoader(
            train_dataset.transform(SSDDefaultTrainTransform(width, height, anchors)),
            batch_size, True, batchify_fn=batchify_fn, last_batch='rollover', num_workers=self.num_workers)
        val_batchify_fn = Tuple(Stack(), Pad(pad_val=-1))
        val_loader = gluon.data.DataLoader(
            val_dataset.transform(SSDDefaultValTransform(width, height)),
            batch_size, False, batchify_fn=val_batchify_fn, last_batch='keep', num_workers=self.num_workers)
        return train_loader, val_loader

    def save_params(self,  current_map, epoch, save_interval, prefix):
        current_map = float(current_map)
        if current_map > self.best_map[0]:
            self.best_map[0] = current_map
            self.net.save_params('{:s}_best.params'.format(prefix, epoch, current_map))
            with open(prefix + '_best_map.log', 'a') as f:
                f.write('{:04d}:\t{:.4f}\n'.format(epoch, current_map))
        if save_interval and epoch % save_interval == 0:
            self.net.save_params('{:s}_{:04d}_{:.4f}.params'.format(prefix, epoch, current_map))

    def validate(self, eval_metric):
        eval_metric.reset()
        # set nms threshold and topk constraint
        self.net.set_nms(nms_thresh=0.45, nms_topk=400)
        self.net.hybridize(static_alloc=True, static_shape=True)
        for batch in self.val_data:
            data = gluon.utils.split_and_load(batch[0], ctx_list=self.ctx, batch_axis=0, even_split=False)
            label = gluon.utils.split_and_load(batch[1], ctx_list=self.ctx, batch_axis=0, even_split=False)
            det_bboxes = []
            det_ids = []
            det_scores = []
            gt_bboxes = []
            gt_ids = []
            gt_difficults = []
            for x, y in zip(data, label):
                # get prediction results
                ids, scores, bboxes = self.net(x)
                det_ids.append(ids)
                det_scores.append(scores)
                # clip to image size
                det_bboxes.append(bboxes.clip(0, batch[0].shape[2]))
                # split ground truths
                gt_ids.append(y.slice_axis(axis=-1, begin=4, end=5))
                gt_bboxes.append(y.slice_axis(axis=-1, begin=0, end=4))
                gt_difficults.append(y.slice_axis(axis=-1, begin=5, end=6) if y.shape[-1] > 5 else None)

            # update metric
            eval_metric.update(det_bboxes, det_ids, det_scores, gt_bboxes, gt_ids, gt_difficults)
        return eval_metric.get()

    def train(self):
        # val_data = get_dataloader(net, val_dataset, 512, 12, 0)

        # lr decay policy
        lr_decay = float(0.1)
        lr_steps = sorted([float(ls) for ls in '160,200'.split(',') if ls.strip()])

        for epoch in range(0, 20):
            while lr_steps and epoch >= lr_steps[0]:
                new_lr = self.trainer.learning_rate * lr_decay
                lr_steps.pop(0)
                self.trainer.set_learning_rate(new_lr)
                print("[Epoch {}] Set learning rate to {}".format(epoch, new_lr))

            self.ce_metric.reset()
            self.smoothl1_metric.reset()
            tic = time.time()
            btic = time.time()
            self.net.hybridize(static_alloc=True, static_shape=True)
            for i, batch in enumerate(self.train_data):
                batch_size = batch[0].shape[0]
                data = gluon.utils.split_and_load(batch[0], ctx_list=self.ctx, batch_axis=0)
                cls_targets = gluon.utils.split_and_load(batch[1], ctx_list=self.ctx, batch_axis=0)
                box_targets = gluon.utils.split_and_load(batch[2], ctx_list=self.ctx, batch_axis=0)
                with autograd.record():
                    cls_preds = []
                    box_preds = []
                    for x in data:
                        cls_pred, box_pred, _ = self.net(x)
                        cls_preds.append(cls_pred)
                        box_preds.append(box_pred)
                    sum_loss, cls_loss, box_loss = self.mbox_loss(
                        cls_preds, box_preds, cls_targets, box_targets)
                    autograd.backward(sum_loss)
                # since we have already normalized the loss, we don't want to normalize
                # by batch-size anymore
                self.trainer.step(1)
                self.ce_metric.update(0, [l * batch_size for l in cls_loss])
                self.smoothl1_metric.update(0, [l * batch_size for l in box_loss])
                name1, loss1 = self.ce_metric.get()
                name2, loss2 = self.smoothl1_metric.get()
                if i % 20 == 0:
                    print('[Epoch {}][Batch {}], Speed: {:.3f} samples/sec, {}={:.3f}, {}={:.3f}'.format(
                        epoch, i, batch_size / (time.time() - btic), name1, loss1, name2, loss2))
                btic = time.time()

            map_name, mean_ap = self.validate( self.val_metric)
            val_msg = '\n'.join(['{}={}'.format(k, v) for k, v in zip(map_name, mean_ap)])
            print('[Epoch {}] Validation: \n{}'.format(epoch, val_msg))
            current_map = float(mean_ap[-1])
            # save_params(net, best_map, current_map, epoch, 10, "D:/abner/project/pyproject/canvas/src/sava_params/sd_resnet34")

        #############################################################################################
        # Save finetuned weights to disk
        # net.save_parameters('ssd_resnet.params')
        self.net.export(self.export_model_file)
        #############################################################################################








# def test():
#     root = "D:/abner/project/pyproject/canvas/src/sava_params/"
#     net = gluon.SymbolBlock.imports(symbol_file=root+'ssd_resnet34_914_id-symbol.json',
#                                     input_names=['data'],  ctx=ctx)
#     # net = gcv.model_zoo.get_model('ssd_512_mobilenet1.0_custom',root=root, classes=classes, pretrained_base=False)
#     net.load_parameters(root+'ssd_resnet34_914_id-0000.params')
#     x, image = gcv.data.transforms.presets.ssd.load_test(
#         'D:/abner/project/dataset/idcard/VOC2007/JPEGImages/3.jpg', 512)
#     cid, score, bbox = net(x)
#     print("classes",classes)
#     ax = viz.plot_bbox(image, bbox[0], score[0], cid[0], class_names=classes)
#     plt.show()


# test()

if __name__ == '__main__':
    dataset_root = "D:/abner/project/dataset/QAOCR"
    trainer = MXTrainOb(dataset_root)
    trainer.train()
