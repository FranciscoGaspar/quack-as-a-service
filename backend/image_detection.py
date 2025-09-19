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

def detect_objects_in_image(image, text_queries, threshold=0.3):
    """
    Detect objects in an image using the transformer model
    
    Args:
        image: PIL Image object
        text_queries: String with text queries (e.g., "a mask. a glove. a hairnet.")
        threshold: Detection threshold
    
    Returns:
        Detection results
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
    
    return results

def visualize_detections(image, results, text_queries):
    """
    Visualize object detection results by drawing bounding boxes on the image.
    
    Args:
        image: PIL Image object
        results: Detection results from the model
        text_queries: List of text queries used for detection
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.imshow(image)
    
    # Define colors for different object types
    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'brown']
    
    for result in results:
        boxes = result['boxes']
        scores = result['scores']
        labels = result['labels']
        
        for i, (box, score, label) in enumerate(zip(boxes, scores, labels)):
            # Convert box coordinates (x1, y1, x2, y2) to matplotlib format
            x1, y1, x2, y2 = box
            width = x2 - x1
            height = y2 - y1
            
            # Create rectangle patch
            color = colors[i % len(colors)]
            rect = patches.Rectangle((x1, y1), width, height, 
                                   linewidth=2, edgecolor=color, facecolor='none')
            ax.add_patch(rect)
            
            # Add label and confidence score
            ax.text(x1, y1-5, f'{label}: {score:.3f}', 
                   fontsize=10, color=color, weight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    ax.set_title(f'Object Detection Results\nQueries: {", ".join(text_queries)}', 
                fontsize=14, weight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.show()

def main():
    """Main function to run the original image detection script"""

    image_urls = [
        "https://www.news-medical.net/image-handler/picture/2021/11/shutterstock_1118088002.jpg",
        "https://t3.ftcdn.net/jpg/08/34/47/68/360_F_834476874_gZcJ7MhKJZUWU6RFEYthy4oEtNo6Iris.jpg"
    ]

    for image_url in image_urls:
        image = Image.open(requests.get(image_url, stream=True).raw)

        # VERY important: text queries need to be lowercased + end with a dot
        text = "a mask. a glove. a hairnet."

        # Use the modular function
        results = detect_objects_in_image(image, text, threshold=0.3)

        # Print the detection results
        for result in results:
            print(f"Detected {len(result['boxes'])} objects:")
            for i, (box, score, label) in enumerate(zip(result['boxes'], result['scores'], result['labels'])):
                print(f"  {i+1}. {label}: {score:.3f} confidence")
                print(f"     Box coordinates: {box}")

        # Visualize the detections
        text_queries = text.split('.')[:-1]  # Remove empty string from split
        visualize_detections(image, results, text_queries)

if __name__ == "__main__":
    main()
