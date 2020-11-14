#MIT License
#
#Copyright (c) 2019 YangYun
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
import os
import cv2
import random
import colorsys
import numpy as np
import tensorflow as tf
from PIL import Image
import ck_utils
#taken from original code
#TODO modify for batch. but want to test if all works before.
def ck_custom_preprocess(image_files, iter_num,processed_image_ids,params):
    image_file = image_files[iter_num]
    image_id = ck_utils.filename_to_id(image_file, params["DATASET_TYPE"])
    processed_image_ids.append(image_id)
    image_path = os.path.join(params["IMAGES_DIR"], image_file)
    orig_image = cv2.imread(image_path)
    orig_image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
    original_image_size = orig_image.shape[:2]
    image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB).astype(np.float32)

    ih, iw    = 416,416   ##They are equal, and the model requires that size so must be hardcoded.
    h,  w, _  = image.shape

    scale = min(iw/w, ih/h)
    nw, nh  = int(scale * w), int(scale * h)
    image_resized = cv2.resize(image, (nw, nh))

    image_paded = np.full(shape=[ih, iw, 3], fill_value=128.0)
    dw, dh = (iw - nw) // 2, (ih-nh) // 2
    image_paded[dh:nh+dh, dw:nw+dw, :] = image_resized
    image_paded = image_paded / 255.
    image_paded = image_paded[np.newaxis, ...]
    return image_paded,processed_image_ids,original_image_size,orig_image


#keeping the distinction between input and output tensors, as in ck detect program. 
def ck_custom_get_tensors():
    image_tensor ="input/input_data:0"
    return_elements = ["pred_sbbox/concat_2:0", "pred_mbbox/concat_2:0", "pred_lbbox/concat_2:0"]
    graph = tf.compat.v1.get_default_graph()
    ops = graph.get_operations()
    all_tensor_names = {output.name for op in ops for output in op.outputs}
    tensor_dict = {}
    for tensor_name in return_elements:
        if tensor_name in all_tensor_names:
           tensor_dict[tensor_name] = graph.get_tensor_by_name(tensor_name)

    image_tensor = graph.get_tensor_by_name(image_tensor)
    return tensor_dict, image_tensor



def bboxes_iou(boxes1, boxes2):

    boxes1 = np.array(boxes1)
    boxes2 = np.array(boxes2)

    boxes1_area = (boxes1[..., 2] - boxes1[..., 0]) * (boxes1[..., 3] - boxes1[..., 1])
    boxes2_area = (boxes2[..., 2] - boxes2[..., 0]) * (boxes2[..., 3] - boxes2[..., 1])

    left_up       = np.maximum(boxes1[..., :2], boxes2[..., :2])
    right_down    = np.minimum(boxes1[..., 2:], boxes2[..., 2:])                                      
    
    inter_section = np.maximum(right_down - left_up, 0.0)                                             
    inter_area    = inter_section[..., 0] * inter_section[..., 1]                                     
    union_area    = boxes1_area + boxes2_area - inter_area
    ious          = np.maximum(1.0 * inter_area / union_area, np.finfo(np.float32).eps)               
    
    return ious        



def nms(bboxes, iou_threshold, sigma=0.3, method='nms'):                                              
    """
    :param bboxes: (xmin, ymin, xmax, ymax, score, class)                                             

    Note: soft-nms, https://arxiv.org/pdf/1704.04503.pdf                                              
          https://github.com/bharatsingh430/soft-nms
    """
    classes_in_img = list(set(bboxes[:, 5]))                                                          
    best_bboxes = []

    for cls in classes_in_img:
        cls_mask = (bboxes[:, 5] == cls)
        cls_bboxes = bboxes[cls_mask]

        while len(cls_bboxes) > 0:
            max_ind = np.argmax(cls_bboxes[:, 4])
            best_bbox = cls_bboxes[max_ind]
            best_bboxes.append(best_bbox)
            cls_bboxes = np.concatenate([cls_bboxes[: max_ind], cls_bboxes[max_ind + 1:]])
            iou = bboxes_iou(best_bbox[np.newaxis, :4], cls_bboxes[:, :4])
            weight = np.ones((len(iou),), dtype=np.float32)

            assert method in ['nms', 'soft-nms']

            if method == 'nms':
                iou_mask = iou > iou_threshold
                weight[iou_mask] = 0.0

            if method == 'soft-nms':
                weight = np.exp(-(1.0 * iou ** 2 / sigma))

            cls_bboxes[:, 4] = cls_bboxes[:, 4] * weight
            score_mask = cls_bboxes[:, 4] > 0.
            cls_bboxes = cls_bboxes[score_mask]

    return best_bboxes


#mimicks the original ck function to save to file the bounding boxes. first line is original image size, then one line per detection, with x1,y1,x2,y2,score,class_id,class_name.
def ck_custom_save_txt(image_file, image_size, bboxes, category_index,DETECTIONS_OUT_DIR):
    (im_width, im_height) = image_size
    file_name = os.path.splitext(image_file)[0]
    res_file = os.path.join(DETECTIONS_OUT_DIR, file_name) + '.txt'
    with open(res_file, 'w') as f:
        f.write('{:d} {:d}\n'.format(im_width, im_height))
        for entry in bboxes:
            if 'display_name' in category_index[entry[5]]:
                class_name = category_index[entry[5]]['display_name']
            else:
                class_name = category_index[entry[5]]['name']
            f.write("%.2f %.2f %.2f %.2f %.3f %d %s \n" % (entry[0] ,entry[1],entry[2],entry[3],entry[4],entry[5],class_name))


#for this function I will use the ck standard label-class structure, thus slightly modifing the original code. I will however maintain the original opencv printing function, working with the postprocessed tensor of the yolo network (thus keeping opencv)
def ck_custom_save_images(image, bboxes, category_index, show_label=True):
    """
    bboxes: [x_min, y_min, x_max, y_max, probability, cls_id] format coordinates.
    """
    num_classes = max(category_index.keys())
    image_h, image_w, _ = image.shape
    hsv_tuples = [(1.0 * x / num_classes, 1., 1.) for x in range(num_classes)]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))

    random.seed(0)
    random.shuffle(colors)
    random.seed(None)

    for i, bbox in enumerate(bboxes):
        coor = np.array(bbox[:4], dtype=np.int32)
        fontScale = 0.5
        score = bbox[4]
        class_ind = int(bbox[5])
        bbox_color = colors[class_ind]
        bbox_thick = int(0.6 * (image_h + image_w) / 600)
        c1, c2 = (coor[0], coor[1]), (coor[2], coor[3])
        cv2.rectangle(image, c1, c2, bbox_color, bbox_thick)
        if 'display_name' in category_index[class_ind]:
            class_name = category_index[class_ind]['display_name']
        else:
            class_name = category_index[class_ind]['name']

        if show_label:
            bbox_mess = '%s: %.2f' % (class_name, score)
            t_size = cv2.getTextSize(bbox_mess, 0, fontScale, thickness=bbox_thick//2)[0]
            cv2.rectangle(image, c1, (c1[0] + t_size[0], c1[1] - t_size[1] - 3), bbox_color, -1)  # filled

            cv2.putText(image, bbox_mess, (c1[0], c1[1]-2), cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale, (0, 0, 0), bbox_thick//2, lineType=cv2.LINE_AA)

    return image




#uses postprocess code from the implementation of yolo
#modified to adapt to hooks, so it will comprehend the tensor concatenation and reshaping, and the print to file. All the functionality are taken from the original code, and adapted.
#added the remapping of the ids to the ck postprocessing standard ids.
#TODO batch support
#resize dim comes with a tuple width,height. and they MUST be equal, otherwise should already have failed in the preprocess
def ck_custom_postprocess(image_files,iter_num, image_size,image_data,dummy, output_dict, category_index,params,score_threshold = 0.3):
#pred_bbox, org_img_shape, input_size, score_threshold):
    ##first step: concatenate the three tensors
    num_classes = len(category_index.keys())
    pred_bbox = np.concatenate([np.reshape(output_dict["pred_sbbox/concat_2:0"], (-1, 5 + num_classes)),
                                np.reshape(output_dict["pred_mbbox/concat_2:0"], (-1, 5 + num_classes)),
                                np.reshape(output_dict["pred_lbbox/concat_2:0"], (-1, 5 + num_classes))], axis=0)


    valid_scale=[0, np.inf]
    pred_bbox = np.array(pred_bbox)

    pred_xywh = pred_bbox[:, 0:4]
    pred_conf = pred_bbox[:, 4]
    pred_prob = pred_bbox[:, 5:]
    # # (1) (x, y, w, h) --> (xmin, ymin, xmax, ymax)
    pred_coor = np.concatenate([pred_xywh[:, :2] - pred_xywh[:, 2:] * 0.5,
                                pred_xywh[:, :2] + pred_xywh[:, 2:] * 0.5], axis=-1)
    # # (2) (xmin, ymin, xmax, ymax) -> (xmin_org, ymin_org, xmax_org, ymax_org)
    org_h, org_w = image_size
    resize_dim = 416,416   ##They are equal.
    resize_ratio = min(resize_dim[0] / org_w, resize_dim[1] / org_h)

    dw = (resize_dim[0] - resize_ratio * org_w) / 2
    dh = (resize_dim[0] - resize_ratio * org_h) / 2

    pred_coor[:, 0::2] = 1.0 * (pred_coor[:, 0::2] - dw) / resize_ratio
    pred_coor[:, 1::2] = 1.0 * (pred_coor[:, 1::2] - dh) / resize_ratio

    # # (3) clip some boxes those are out of range
    pred_coor = np.concatenate([np.maximum(pred_coor[:, :2], [0, 0]),
                                np.minimum(pred_coor[:, 2:], [org_w - 1, org_h - 1])], axis=-1)
    invalid_mask = np.logical_or((pred_coor[:, 0] > pred_coor[:, 2]), (pred_coor[:, 1] > pred_coor[:, 3]))
    pred_coor[invalid_mask] = 0

    # # (4) discard some invalid boxes
    bboxes_scale = np.sqrt(np.multiply.reduce(pred_coor[:, 2:4] - pred_coor[:, 0:2], axis=-1))
    scale_mask = np.logical_and((valid_scale[0] < bboxes_scale), (bboxes_scale < valid_scale[1]))

    # # (5) discard some boxes with low scores
    classes = np.argmax(pred_prob, axis=-1)
    scores = pred_conf * pred_prob[np.arange(len(pred_coor)), classes]
    score_mask = scores > score_threshold
    mask = np.logical_and(scale_mask, score_mask)
    array_of_ids = [1,2,3,4,5,6,7,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,27,28,31,32,33,34,35,36,37,38,39,40,41,42,43,44,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,67,70,72,73,74,75,76,77,78,79,80,81,82,84,85,86,87,88,89,90]
    correct_labels = lambda x : array_of_ids[x]
    classes = np.array([correct_labels(x) for x in classes])

    coors, scores, classes = pred_coor[mask], scores[mask], classes[mask]

    bboxes= np.concatenate([coors, scores[:, np.newaxis], classes[:, np.newaxis]], axis=-1)
    bboxes= nms (bboxes, 0.45, method='nms')
    ck_custom_save_txt(image_files[iter_num], image_size,bboxes,category_index,params["DETECTIONS_OUT_DIR"])
    if not params["SAVE_IMAGES"]:
        return
    else:
        image = ck_custom_save_images(image_data,bboxes,category_index)
        image = Image.fromarray(image)
        image.save(image_files[iter_num])

###### BATCH PROCESSING FUNCTIONS

def ck_custom_preprocess_batch(image_files, iter_num,processed_image_ids,params):
    batch_data = []
    batch_sizes = []
    orig_images = []
    for img in range(params["BATCH_SIZE"]):
        image_file = image_files[iter_num*params["BATCH_SIZE"]+img]
        image_id = ck_utils.filename_to_id(image_file, params["DATASET_TYPE"])
        processed_image_ids.append(image_id)
        image_path = os.path.join(params["IMAGES_DIR"], image_file)
        orig_image = cv2.imread(image_path)
        orig_image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
        orig_images.append(orig_image)
        batch_sizes.append(orig_image.shape[:2])
        image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB).astype(np.float32)
 
        ih, iw    = 416,416   ##They are equal.
        h,  w, _  = image.shape
 
        scale = min(iw/w, ih/h)
        nw, nh  = int(scale * w), int(scale * h)
        image_resized = cv2.resize(image, (nw, nh))
 
        image_paded = np.full(shape=[ih, iw, 3], fill_value=128.0)
        dw, dh = (iw - nw) // 2, (ih-nh) // 2
        image_paded[dh:nh+dh, dw:nw+dw, :] = image_resized
        image_paded = image_paded / 255.
        print(np.shape(image_paded))
        #image_paded = image_paded[np.newaxis, ...]
        #print(np.shape(image_paded))
        batch_data.append(image_paded)
    return batch_data,processed_image_ids,batch_sizes,orig_images




















def ck_custom_postprocess_batch(image_files,iter_num, image_size,image_data,dummy, output_dict, category_index,params,score_threshold = 0.3):
#pred_bbox, org_img_shape, input_size, score_threshold):
    ##first step: concatenate the three tensors

    for img in range(params["BATCH_SIZE"]):
        num_classes = len(category_index.keys())
        pred_bbox = np.concatenate([np.reshape(output_dict["pred_sbbox/concat_2:0"][img], (-1, 5 + num_classes)),
                                    np.reshape(output_dict["pred_mbbox/concat_2:0"][img], (-1, 5 + num_classes)),
                                    np.reshape(output_dict["pred_lbbox/concat_2:0"][img], (-1, 5 + num_classes))], axis=0)
 
 
        valid_scale=[0, np.inf]
        pred_bbox = np.array(pred_bbox)
 
        pred_xywh = pred_bbox[:, 0:4]
        pred_conf = pred_bbox[:, 4]
        pred_prob = pred_bbox[:, 5:]
        # # (1) (x, y, w, h) --> (xmin, ymin, xmax, ymax)
        pred_coor = np.concatenate([pred_xywh[:, :2] - pred_xywh[:, 2:] * 0.5,
                                    pred_xywh[:, :2] + pred_xywh[:, 2:] * 0.5], axis=-1)
        # # (2) (xmin, ymin, xmax, ymax) -> (xmin_org, ymin_org, xmax_org, ymax_org)
        org_h, org_w = image_size[img]
        resize_dim = 416,416   ##They are equal.
        resize_ratio = min(resize_dim[0] / org_w, resize_dim[1] / org_h)
 
        dw = (resize_dim[0] - resize_ratio * org_w) / 2
        dh = (resize_dim[0] - resize_ratio * org_h) / 2
 
        pred_coor[:, 0::2] = 1.0 * (pred_coor[:, 0::2] - dw) / resize_ratio
        pred_coor[:, 1::2] = 1.0 * (pred_coor[:, 1::2] - dh) / resize_ratio
 
        # # (3) clip some boxes those are out of range
        pred_coor = np.concatenate([np.maximum(pred_coor[:, :2], [0, 0]),
                                    np.minimum(pred_coor[:, 2:], [org_w - 1, org_h - 1])], axis=-1)
        invalid_mask = np.logical_or((pred_coor[:, 0] > pred_coor[:, 2]), (pred_coor[:, 1] > pred_coor[:, 3]))
        pred_coor[invalid_mask] = 0
 
        # # (4) discard some invalid boxes
        bboxes_scale = np.sqrt(np.multiply.reduce(pred_coor[:, 2:4] - pred_coor[:, 0:2], axis=-1))
        scale_mask = np.logical_and((valid_scale[0] < bboxes_scale), (bboxes_scale < valid_scale[1]))
 
        # # (5) discard some boxes with low scores
        classes = np.argmax(pred_prob, axis=-1)
        scores = pred_conf * pred_prob[np.arange(len(pred_coor)), classes]
        score_mask = scores > score_threshold
        mask = np.logical_and(scale_mask, score_mask)
        array_of_ids = [1,2,3,4,5,6,7,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,27,28,31,32,33,34,35,36,37,38,39,40,41,42,43,44,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,67,70,72,73,74,75,76,77,78,79,80,81,82,84,85,86,87,88,89,90]
        correct_labels = lambda x : array_of_ids[x]
        classes = np.array([correct_labels(x) for x in classes])
 
        coors, scores, classes = pred_coor[mask], scores[mask], classes[mask]
 
        bboxes= np.concatenate([coors, scores[:, np.newaxis], classes[:, np.newaxis]], axis=-1)
        bboxes= nms (bboxes, 0.45, method='nms')
        ck_custom_save_txt(image_files[iter_num*params["BATCH_SIZE"]+img], image_size[img],bboxes,category_index,params["DETECTIONS_OUT_DIR"])
        if not params["SAVE_IMAGES"]:
            continue
        else:
            image = ck_custom_save_images(image_data[img],bboxes,category_index)
            image = Image.fromarray(image)
            image.save(image_files[iter_num*params["BATCH_SIZE"]+img])

