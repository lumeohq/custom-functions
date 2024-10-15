from lumeopipeline import VideoFrame
import numpy as np
import torch
import torchvision

# Global variables and one-time initialization
node = {
    "model_id": None,
    "model_node_id": None,
    "output_layer_name": "output0",
    "labels": [],
    "nms_threshold": 0.5,
    "score_threshold": 0.4,
    "min_object_size": 5,
    "device": None,
    "initialized": False
}

def yolo_detect(inference_output):
    output = inference_output.to(node['device'])
    boxes, scores, class_probs = output[..., :4], output[..., 4], output[..., 5:]
    classes = torch.argmax(class_probs, dim=-1)
    x, y, w, h = boxes.unbind(-1)
    boxes = torch.stack([x - w/2, y - h/2, x + w/2, y + h/2], dim=-1)
    return boxes, classes, scores

def process_frame(frame: VideoFrame, **kwargs) -> bool:
    
    output_objects = []
    meta = frame.meta()
    detected_objects = meta.get_field("objects")
    
    if not node['initialized']:
        initialize(**kwargs)
    
    with frame.data() as mat:
        height, width = mat.shape[:2]

        # Process frame level tensors        
        tensors = frame.tensors()
        output_data = next((np.asarray(layer.data).reshape(layer.dimensions)
                            for tensor in tensors if (tensor.source_node_id == node['model_node_id'] or (tensor.model_id and tensor.model_id == node['model_id']))
                            for layer in tensor.layers if layer.name == node['output_layer_name']), None)
        
        if output_data is not None:
            output_objects.extend(extract_objects(output_data, height, width))

        # Process object level tensors if the model runs as a secondary model
        object_tensors = frame.object_tensors()
        if len(detected_objects) > 0 and len(object_tensors) > 0:
            for obj, obj_tensor in zip(detected_objects, object_tensors):                        
                output_data = next((np.asarray(layer.data).reshape(layer.dimensions)
                                    for tensor in obj_tensor.tensors
                                    if (tensor.source_node_id == node['model_node_id'] or (tensor.model_id and tensor.model_id == node['model_id']))
                                    for layer in tensor.layers
                                    if layer.name == node['output_layer_name']), None)
                if output_data is not None:
                    extracted_objects = extract_objects(output_data, obj['rect']['height'], obj['rect']['width'])
                    for extracted_obj in extracted_objects:
                        extracted_obj['rect']['left'] += obj['rect']['left']
                        extracted_obj['rect']['top'] += obj['rect']['top']
                    output_objects.extend(extracted_objects)
                                        
    if output_objects:
        detected_objects.extend(output_objects)
        save_metadata(frame, detected_objects)

    return True

def initialize(**kwargs):
    configuration = kwargs.get('configuration', {})
    node['model_id'] = kwargs.get('model_id', configuration.get('model_id', None))
    node['model_node_id'] = kwargs.get('model_node_id', configuration.get('model_node_id', None))
    node['output_layer_name'] = kwargs.get('output_layer_name', configuration.get('output_layer_name', 'output0'))
    node['labels'] = kwargs.get('labels', configuration.get('labels', []))
    node['nms_threshold'] = kwargs.get('nms_threshold', configuration.get('nms_threshold', 0.5))
    node['score_threshold'] = kwargs.get('score_threshold', configuration.get('score_threshold', 0.4))
    node['min_object_size'] = kwargs.get('min_object_size', configuration.get('min_object_size', 5))
    
    if torch.cuda.is_available():
        gpu_id = kwargs.get('gpu_id', None)
        node['device'] = torch.device('cuda') if gpu_id is None else torch.device(f'cuda:{gpu_id}')
    else:
        node['device'] = torch.device('cpu')
    
    node['initialized'] = True
    
    return

def extract_objects(output_data, height, width):
    detected_objects = []
    xyxy, classes, scores = yolo_detect(torch.from_numpy(output_data))
    
    if xyxy.numel() > 0:
        nms_output = torchvision.ops.nms(xyxy, scores, node['nms_threshold'])
        xyxy_normalized = xyxy[nms_output] / 640
        
        mask = (scores[nms_output] > node['score_threshold'])
        xyxy_filtered = xyxy_normalized[mask]
        classes_filtered = classes[nms_output][mask]
        scores_filtered = scores[nms_output][mask]
        
        obj_dims = torch.stack([
            (xyxy_filtered[:, 2] - xyxy_filtered[:, 0]) * width,
            (xyxy_filtered[:, 3] - xyxy_filtered[:, 1]) * height
        ], dim=-1)
        
        size_mask = (obj_dims > node['min_object_size']).all(dim=-1)
        xyxy_final = xyxy_filtered[size_mask]
        classes_final = classes_filtered[size_mask]
        scores_final = scores_filtered[size_mask]
        
        detected_objects = [
            {
                "label": node['labels'][int(class_id)],
                "class_id": int(class_id),
                "probability": float(score),
                "rect": {
                    "left": int(max(1, bbox[0] * width)),
                    "top": int(max(1, bbox[1] * height)),
                    "width": int(min(width, (bbox[2] - bbox[0]) * width)),
                    "height": int(min(height, (bbox[3] - bbox[1]) * height))
                }
            }
            for bbox, class_id, score in zip(xyxy_final.cpu().numpy(), classes_final.cpu().numpy(), scores_final.cpu().numpy())
        ]    
        
    return detected_objects

def save_metadata(frame, detected_objects):
    try:
        meta = frame.meta()
        objects = meta.get_field("objects")
        objects.extend(detected_objects)
        meta.set_field("objects", objects)
        meta.save()
    except Exception as error:
        print(f"Error saving metadata: {error}")