import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection 

# Global model variables
model_id = "IDEA-Research/grounding-dino-base"
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = None
model = None

def initialize_model():
    """Initialize the model and processor"""
    global processor, model
    if processor is None or model is None:
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(device)
    return processor, model

def detect_objects_in_image(image, text_queries, threshold=0.32):
    """
    Detect objects in an image using the transformer model
    
    Args:
        image: PIL Image object
        text_queries: String with text queries (e.g., "a mask. a glove. a hairnet.")
        threshold: Detection threshold (minimum 0.32 confidence required)
    
    Returns:
        Detection results with improved filtering
    """
    proc, mod = initialize_model()
    
    inputs = proc(images=image, text=text_queries, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = mod(**inputs)
    
    results = proc.post_process_grounded_object_detection(
        outputs,
        inputs.input_ids,
        text_threshold=threshold,
        target_sizes=[image.size[::-1]]
    )
    
    filtered_results = []
    for result in results:
        filtered_boxes = []
        filtered_scores = []
        filtered_labels = []
        
        # Use text_labels instead of labels to avoid deprecation warning
        labels_key = 'text_labels' if 'text_labels' in result else 'labels'
        
        for box, score, label in zip(result['boxes'], result['scores'], result[labels_key]):
            if score >= threshold:
                filtered_boxes.append(box)
                filtered_scores.append(score)
                filtered_labels.append(label)
        
        filtered_result = {
            'boxes': filtered_boxes,
            'scores': filtered_scores,
            'labels': filtered_labels
        }
        filtered_results.append(filtered_result)
    
    return filtered_results

def combine_detection_results(all_results):
    """
    Combine multiple detection results and remove duplicates based on box overlap.
    
    Args:
        all_results: List of detection results from multiple queries
    
    Returns:
        Combined and deduplicated results
    """
    if not all_results:
        return []
    
    combined_boxes = []
    combined_scores = []
    combined_labels = []
    
    for result in all_results:
        combined_boxes.extend(result['boxes'])
        combined_scores.extend(result['scores'])
        combined_labels.extend(result['labels'])
    
    # Remove duplicates based on box overlap
    unique_results = []
    used_indices = set()
    
    for i, (box1, score1, label1) in enumerate(zip(combined_boxes, combined_scores, combined_labels)):
        if i in used_indices:
            continue
            
        # Check for overlapping boxes
        is_duplicate = False
        for j, (box2, score2, label2) in enumerate(zip(combined_boxes, combined_scores, combined_labels)):
            if j <= i or j in used_indices:
                continue
                
            # Calculate IoU (Intersection over Union)
            iou = calculate_iou(box1, box2)
            if iou > 0.5 and label1.lower() == label2.lower():  # Same label and high overlap
                is_duplicate = True
                # Keep the one with higher score
                if score1 < score2:
                    used_indices.add(i)
                else:
                    used_indices.add(j)
                break
        
        if not is_duplicate:
            unique_results.append((box1, score1, label1))
    
    # Convert back to result format
    if unique_results:
        boxes, scores, labels = zip(*unique_results)
        return [{
            'boxes': list(boxes),
            'scores': list(scores),
            'labels': list(labels)
        }]
    else:
        return [{'boxes': [], 'scores': [], 'labels': []}]

def calculate_iou(box1, box2):
    """
    Calculate Intersection over Union (IoU) of two bounding boxes.
    
    Args:
        box1, box2: Bounding boxes as tensors or lists [x1, y1, x2, y2]
    
    Returns:
        IoU value between 0 and 1
    """
    # Convert to numpy if needed
    if hasattr(box1, 'cpu'):
        box1 = box1.cpu().numpy()
    if hasattr(box2, 'cpu'):
        box2 = box2.cpu().numpy()
    
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    # Calculate intersection
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i <= x1_i or y2_i <= y1_i:
        return 0.0
    
    intersection = (x2_i - x1_i) * (y2_i - y1_i)
    
    # Calculate union
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0

def analyze_detection_results(results, required_items):
    """
    Analyze detection results to determine which required items were found and which are missing.
    
    Args:
        results: Detection results from the model
        required_items: List of required items to check for (e.g., ['a mask', 'a glove', 'a hairnet'])
    
    Returns:
        dict: Analysis results with found_items, missing_items, and confidence_scores
    """
    found_items = {}
    missing_items = []
    confidence_scores = {}
    
    # Extract all detected labels and their scores
    detected_labels = []
    for result in results:
        for label, score in zip(result['labels'], result['scores']):
            detected_labels.append(label.lower().strip())
            confidence_scores[label.lower().strip()] = score
    
    # Check which required items were found
    for item in required_items:
        item_found = False
        best_score = 0
        best_label = None
        
        # Extract the core item name (remove "a " prefix)
        core_item = item.lower().replace('a ', '').strip()
        
        # Check if any detected label matches this required item
        for detected_label in detected_labels:
            # More flexible matching - check for partial matches
            detected_core = detected_label.replace('a ', '').strip()
            
            # Check various matching patterns
            if (core_item in detected_core or 
                detected_core in core_item or
                core_item == detected_core or
                item.lower() in detected_label or
                detected_label in item.lower()):
                item_found = True
                if confidence_scores[detected_label] > best_score:
                    best_score = confidence_scores[detected_label]
                    best_label = detected_label
        
        if item_found:
            found_items[item] = {
                'confidence': best_score,
                'detected_as': best_label
            }
        else:
            missing_items.append(item)
    
    return {
        'found_items': found_items,
        'missing_items': missing_items,
        'total_detected': len(detected_labels),
        'compliance_status': len(missing_items) == 0
    }

def _draw_detection_annotations(ax, image, results, text_queries, missing_items):
    """
    Helper function to draw detection annotations on a matplotlib axis.
    Contains all the drawing logic extracted from visualize_detections.
    """
    # Define specific colors for each item type
    item_colors = {
        'glove': 'orange',
        'gloves': 'orange',
        'mask': 'blue',
        'masks': 'blue',
        'hairnet': 'white',
        'hairnets': 'white'
    }
    
    for result in results:
        boxes = result['boxes']
        scores = result['scores']
        labels = result['labels']
        
        for i, (box, score, label) in enumerate(zip(boxes, scores, labels)):
            # Convert box coordinates (x1, y1, x2, y2) to matplotlib format
            x1, y1, x2, y2 = box
            width = x2 - x1
            height = y2 - y1
            
            # Determine color based on label
            label_lower = label.lower().strip()
            color = 'red'  # Default color
            
            # Check for specific item types
            for item_type, item_color in item_colors.items():
                if item_type in label_lower:
                    color = item_color
                    break
            
            # Create rectangle patch
            rect = patches.Rectangle((x1, y1), width, height, 
                                   linewidth=2, edgecolor=color, facecolor='none')
            ax.add_patch(rect)
            
            # Add label and confidence score
            ax.text(x1, y1-5, f'{label}: {score:.3f}', 
                   fontsize=10, color=color, weight='bold',
                   bbox=dict(boxstyle="round,pad=0.32", facecolor='white', alpha=0.8))
    
    # Detect hands and head using the model, then add red squares for missing items
    image_width, image_height = image.size
    
    # Detect body parts
    body_parts_query = "a head. a hand. hands."
    body_parts_results = detect_objects_in_image(image, body_parts_query, threshold=0.3)
    
    # Extract detected body parts
    detected_heads = []
    detected_hands = []
    
    for result in body_parts_results:
        for box, score, label in zip(result['boxes'], result['scores'], result['labels']):
            label_lower = label.lower().strip()
            if 'head' in label_lower:
                detected_heads.append((box, score))
            elif 'hand' in label_lower:
                detected_hands.append((box, score))
    
    # Add red squares for missing items
    for missing_item in missing_items:
        missing_lower = missing_item.lower().strip()
        
        if 'mask' in missing_lower:
            if detected_heads:
                # Use the highest confidence head detection
                best_head = max(detected_heads, key=lambda x: x[1])
                head_box = best_head[0]
                
                # Convert box coordinates
                if hasattr(head_box, 'cpu'):
                    head_box = head_box.cpu().numpy()
                x1, y1, x2, y2 = head_box
                
                # Draw red square around detected head
                head_square = patches.Rectangle((x1, y1), x2-x1, y2-y1, 
                                              linewidth=3, edgecolor='red', facecolor='none')
                ax.add_patch(head_square)
                ax.text(x1, y1-15, 'MISSING MASK', 
                       fontsize=10, color='red', weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            else:
                # Fallback to fixed position if no head detected
                head_size = min(image_width, image_height) * 0.2
                head_x = image_width * 0.35
                head_y = image_height * 0.05
                head_square = patches.Rectangle((head_x, head_y), head_size, head_size, 
                                              linewidth=3, edgecolor='red', facecolor='none')
                ax.add_patch(head_square)
                ax.text(head_x + head_size/2, head_y - 15, 'MISSING MASK', 
                       fontsize=10, color='red', weight='bold', ha='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        if 'hairnet' in missing_lower:
            if detected_heads:
                # Use the highest confidence head detection
                best_head = max(detected_heads, key=lambda x: x[1])
                head_box = best_head[0]
                
                # Convert box coordinates
                if hasattr(head_box, 'cpu'):
                    head_box = head_box.cpu().numpy()
                x1, y1, x2, y2 = head_box
                
                # Draw red square around detected head
                head_square = patches.Rectangle((x1, y1), x2-x1, y2-y1, 
                                              linewidth=3, edgecolor='red', facecolor='none')
                ax.add_patch(head_square)
                ax.text(x1, y1-15, 'MISSING HAIRNET', 
                       fontsize=10, color='red', weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            else:
                # Fallback to fixed position if no head detected
                head_size = min(image_width, image_height) * 0.2
                head_x = image_width * 0.35
                head_y = image_height * 0.05
                head_square = patches.Rectangle((head_x, head_y), head_size, head_size, 
                                              linewidth=3, edgecolor='red', facecolor='none')
                ax.add_patch(head_square)
                ax.text(head_x + head_size/2, head_y - 15, 'MISSING HAIRNET', 
                       fontsize=10, color='red', weight='bold', ha='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        if 'glove' in missing_lower:
            if detected_hands:
                # Draw red squares around detected hands
                for i, (hand_box, score) in enumerate(detected_hands[:2]):  # Limit to 2 hands
                    # Convert box coordinates
                    if hasattr(hand_box, 'cpu'):
                        hand_box = hand_box.cpu().numpy()
                    x1, y1, x2, y2 = hand_box
                    
                    # Draw red square around detected hand
                    hand_square = patches.Rectangle((x1, y1), x2-x1, y2-y1, 
                                                  linewidth=3, edgecolor='red', facecolor='none')
                    ax.add_patch(hand_square)
                
                ax.text(image_width/2, image_height * 0.8, 'MISSING HAND PROTECTION', 
                       fontsize=10, color='red', weight='bold', ha='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            else:
                # Fallback to fixed positions if no hands detected
                hand_size = min(image_width, image_height) * 0.12
                left_hand_x = image_width * 0.1
                left_hand_y = image_height * 0.5
                left_hand_square = patches.Rectangle((left_hand_x, left_hand_y), hand_size, hand_size, 
                                                  linewidth=3, edgecolor='red', facecolor='none')
                ax.add_patch(left_hand_square)
                
                right_hand_x = image_width * 0.8
                right_hand_y = image_height * 0.5
                right_hand_square = patches.Rectangle((right_hand_x, right_hand_y), hand_size, hand_size, 
                                                    linewidth=3, edgecolor='red', facecolor='none')
                ax.add_patch(right_hand_square)
                
                ax.text(image_width/2, left_hand_y + hand_size + 20, 'MISSING HAND PROTECTION', 
                       fontsize=10, color='red', weight='bold', ha='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

    # Add title
    ax.set_title(f'Object Detection Results\nQueries: {", ".join(text_queries)}\nMissing items: {", ".join(missing_items)}', 
                fontsize=14, weight='bold')
    ax.axis('off')


def create_annotated_image(image, results, text_queries, missing_items):
    """
    Create an annotated image with detection boxes and return as bytes.
    Reuses the existing visualization logic from visualize_detections.
    
    Args:
        image: PIL Image object
        results: Detection results from the model
        text_queries: List of text queries used for detection
        missing_items: List of missing items
        
    Returns:
        bytes: Annotated image as bytes for S3 upload
    """
    # Create matplotlib figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    try:
        # Display the image and draw annotations
        ax.imshow(image)
        _draw_detection_annotations(ax, image, results, text_queries, missing_items)
        
        # Save to bytes instead of showing
        from io import BytesIO
        img_buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        image_bytes = img_buffer.getvalue()
        plt.close(fig)  # Important: close the figure to free memory
        
        return image_bytes
        
    except Exception as e:
        plt.close(fig)  # Make sure to close figure even if there's an error
        raise e


def visualize_detections(image, results, text_queries, missing_items):
    """
    Visualize object detection results by drawing bounding boxes on the image.
    Now reuses the same drawing logic as create_annotated_image.
    
    Args:
        image: PIL Image object
        results: Detection results from the model
        text_queries: List of text queries used for detection
        missing_items: List of missing items
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.imshow(image)
    
    # Use the shared drawing logic
    _draw_detection_annotations(ax, image, results, text_queries, missing_items)
    
    plt.tight_layout()
    plt.show()

def main():
    """Main function to run the improved image detection script with better false positive handling"""

    image_urls = [
        # "https://dmrqkbkq8el9i.cloudfront.net/Pictures/2000xAny/4/1/3/182413_factoryworkerstaffproduction_540368.jpg"
        # "https://thumbs.dreamstime.com/b/portrait-food-factory-worker-male-female-thumbs-up-happy-enjoy-working-clean-hygiene-dressing-good-quality-products-220989405.jpg",
        "https://st2.depositphotos.com/3450477/11066/i/950/depositphotos_110669406-stock-photo-young-man-wearing-gloves.jpg"
    ]

    # Define required safety items
    required_items = ['mask', 'glove', 'hairnet']

    text_queries = ". ".join(required_items) + "."
    
    for i, image_url in enumerate(image_urls, 1):
        print(f"\n{'='*60}")
        print(f"ANALYZING IMAGE {i}: {image_url}")
        print(f"{'='*60}")
        
        try:
            image = Image.open(requests.get(image_url, stream=True).raw)

            # Use the predefined text queries for detection
            results = detect_objects_in_image(image, text_queries, threshold=0.4)
            
            # Analyze the results
            analysis = analyze_detection_results(results, required_items)
            
            # Print comprehensive results
            print(f"\nDETECTION SUMMARY:")
            print(f"Total objects detected: {analysis['total_detected']}")
            print(f"Compliance status: {'✅ COMPLIANT' if analysis['compliance_status'] else '❌ NON-COMPLIANT'}")
            
            print(f"\nFOUND ITEMS:")
            if analysis['found_items']:
                for item, details in analysis['found_items'].items():
                    print(f"  ✅ {item.upper()}: {details['confidence']:.3f} confidence (detected as: '{details['detected_as']}')")
            else:
                print("  No required items found with sufficient confidence.")
            
            print(f"\nMISSING ITEMS:")
            if analysis['missing_items']:
                for item in analysis['missing_items']:
                    print(f"  ❌ {item.upper()}: NOT DETECTED")
            else:
                print("  All required items found!")
            
            # Print detailed detection results
            print(f"\nDETAILED DETECTION RESULTS:")
            for result in results:
                if len(result['boxes']) > 0:
                    print(f"High-confidence detections:")
                    for j, (box, score, label) in enumerate(zip(result['boxes'], result['scores'], result['labels'])):
                        print(f"  {j+1}. {label}: {score:.3f} confidence")
                        print(f"     Box coordinates: {box}")
                else:
                    print("  No high-confidence detections found.")
            
            # Visualize the detections
            visualize_detections(image, results, required_items, analysis['missing_items'])
            
        except Exception as e:
            print(f"Error processing image {i}: {str(e)}")
            continue

if __name__ == "__main__":
    main()
