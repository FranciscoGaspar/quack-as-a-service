import cv2
import numpy as np
import torch
from PIL import Image
import os
from datetime import datetime
import time
import threading
import queue
import image_detection

class LiveObjectDetector:
    def __init__(self):
        # Initialize the object detection model using image_detection module
        self.model_id = "IDEA-Research/grounding-dino-base"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("🚀 Initializing Live Object Detection System...")
        print(f"📱 Device: {self.device}")
        print(f"🤖 Model: {self.model_id}")
        
        print("⏳ Loading object detection model...")
        # Initialize the model through image_detection module
        image_detection.initialize_model()
        print("✅ Object detection model loaded successfully!")
        
        # Initialize person detection (using OpenCV's built-in HOG descriptor)
        print("⏳ Initializing person detection...")
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        print("✅ Person detection initialized!")
        
        # Create output directory for saved frames
        self.output_dir = "detected_frames"
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📁 Output directory: {self.output_dir}")
        
        # Detection parameters
        self.person_detection_threshold = 0.2  # Lowered for better detection
        self.object_detection_threshold = 0.2
        self.text_queries = "a mask. a glove. a hairnet."
        
        # Frame processing parameters
        self.frame_skip = 3  # Process every 3rd frame for better responsiveness
        self.last_detection_time = 0
        self.min_detection_interval = 2  # Minimum seconds between object detections
        
        # Countdown timer parameters
        self.countdown_duration = 5  # 5 seconds countdown
        self.countdown_start_time = 0
        self.countdown_active = False
        self.auto_capture_enabled = True
        
        # Async detection parameters
        self.detection_queue = queue.Queue(maxsize=2)  # Limit queue size to prevent memory issues
        self.detection_thread = None
        self.detection_running = False
        self.last_detection_results = []
        self.detection_in_progress = False
        
        # Debug mode
        self.debug_mode = True
        self.show_detection_attempts = True
        
        # Statistics tracking
        self.stats = {
            'total_frames': 0,
            'objects_detected': 0,
            'frames_saved': 0,
            'auto_captures': 0,
            'manual_captures': 0,
            'start_time': time.time()
        }
        
        print(f"🎯 Detection targets: {self.text_queries}")
        print(f"⚙️  Person detection threshold: {self.person_detection_threshold}")
        print(f"⚙️  Object detection threshold: {self.object_detection_threshold}")
        print(f"⚙️  Frame skip interval: {self.frame_skip}")
        print(f"⚙️  Min detection interval: {self.min_detection_interval}s")
        print("=" * 60)
        
        # Start the async detection thread
        self.start_async_detection()
        
    def start_async_detection(self):
        """Start the background detection thread"""
        if not self.detection_running:
            self.detection_running = True
            self.detection_thread = threading.Thread(target=self._detection_worker, daemon=True)
            self.detection_thread.start()
            print("🚀 Async detection thread started!")
    
    def stop_async_detection(self):
        """Stop the background detection thread"""
        if self.detection_running:
            self.detection_running = False
            # Clear the queue to unblock the thread
            while not self.detection_queue.empty():
                try:
                    self.detection_queue.get_nowait()
                except queue.Empty:
                    break
            if self.detection_thread:
                self.detection_thread.join(timeout=1.0)
            print("⏹️ Async detection thread stopped!")
    
    def _detection_worker(self):
        """Background worker thread for object detection"""
        while self.detection_running:
            try:
                # Get frame from queue (blocks until available)
                frame_data = self.detection_queue.get(timeout=1.0)
                if frame_data is None:  # Shutdown signal
                    break
                
                frame, timestamp = frame_data
                self.detection_in_progress = True
                
                # Convert OpenCV frame to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Run object detection
                results = image_detection.detect_objects_in_image(
                    pil_image, 
                    self.text_queries, 
                    threshold=self.object_detection_threshold
                )
                
                # Store results
                self.last_detection_results = results
                self.detection_in_progress = False
                
                # Update statistics
                total_objects = sum(len(result['boxes']) for result in results)
                if total_objects > 0:
                    self.stats['objects_detected'] += total_objects
                    print(f"🎯 Async detection completed: {total_objects} object(s) found")
                
                # Mark task as done
                self.detection_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error in detection worker: {e}")
                self.detection_in_progress = False
                continue
    
    def queue_detection(self, frame):
        """Queue a frame for async object detection"""
        if not self.detection_in_progress and self.detection_queue.qsize() < 2:
            try:
                # Create a copy of the frame to avoid threading issues
                frame_copy = frame.copy()
                timestamp = time.time()
                self.detection_queue.put_nowait((frame_copy, timestamp))
                return True
            except queue.Full:
                print("⚠️ Detection queue full, skipping frame")
                return False
        return False
        
    def detect_persons(self, frame):
        """Detect persons in the frame using multiple methods"""
        if self.debug_mode and self.show_detection_attempts:
            print(f"🔍 Attempting person detection (threshold: {self.person_detection_threshold})")
        
        # Method 1: HOG descriptor (original method)
        boxes_hog, weights_hog = self._detect_persons_hog(frame)
        
        # Method 2: Try with different parameters for better detection
        boxes_hog2, weights_hog2 = self._detect_persons_hog_alternative(frame)
        
        # Combine results (prefer higher confidence detections)
        all_boxes = []
        all_weights = []
        
        # Add HOG detections
        for box, weight in zip(boxes_hog, weights_hog):
            all_boxes.append(box)
            all_weights.append(weight)
        
        # Add alternative HOG detections
        for box, weight in zip(boxes_hog2, weights_hog2):
            all_boxes.append(box)
            all_weights.append(weight)
        
        # Remove duplicate detections (simple overlap check)
        filtered_boxes, filtered_weights = self._remove_duplicate_detections(all_boxes, all_weights)
        
        if len(filtered_boxes) > 0:
            self.stats['persons_detected'] += len(filtered_boxes)
            if self.debug_mode:
                print(f"👤 Detected {len(filtered_boxes)} person(s) with confidence: {[f'{w:.2f}' for w in filtered_weights]}")
        elif self.debug_mode and self.show_detection_attempts:
            print(f"❌ No persons detected (HOG1: {len(boxes_hog)}, HOG2: {len(boxes_hog2)})")
        
        return filtered_boxes, filtered_weights
    
    def _detect_persons_hog(self, frame):
        """Original HOG detection method"""
        # Resize frame for faster processing
        frame_resized = cv2.resize(frame, (640, 480))
        
        # Detect people with original parameters
        boxes, weights = self.hog.detectMultiScale(
            frame_resized, 
            winStride=(8, 8),
            padding=(32, 32),
            scale=1.05,
            hitThreshold=self.person_detection_threshold
        )
        
        # Scale boxes back to original frame size
        scale_x = frame.shape[1] / 640
        scale_y = frame.shape[0] / 480
        boxes = [(int(x * scale_x), int(y * scale_y), int(w * scale_x), int(h * scale_y)) 
                for (x, y, w, h) in boxes]
        
        return boxes, weights
    
    def _detect_persons_hog_alternative(self, frame):
        """Alternative HOG detection with different parameters"""
        # Resize frame for faster processing
        frame_resized = cv2.resize(frame, (640, 480))
        
        # Detect people with more sensitive parameters
        boxes, weights = self.hog.detectMultiScale(
            frame_resized, 
            winStride=(4, 4),  # Smaller stride for better detection
            padding=(16, 16),  # Smaller padding
            scale=1.03,        # Smaller scale steps
            hitThreshold=max(0.1, self.person_detection_threshold - 0.2)  # Lower threshold
        )
        
        # Scale boxes back to original frame size
        scale_x = frame.shape[1] / 640
        scale_y = frame.shape[0] / 480
        boxes = [(int(x * scale_x), int(y * scale_y), int(w * scale_x), int(h * scale_y)) 
                for (x, y, w, h) in boxes]
        
        return boxes, weights
    
    def _remove_duplicate_detections(self, boxes, weights, overlap_threshold=0.3):
        """Remove duplicate detections based on overlap"""
        if len(boxes) == 0:
            return [], []
        
        # Convert to numpy arrays for easier processing
        boxes = np.array(boxes)
        weights = np.array(weights)
        
        # Sort by confidence (weight)
        indices = np.argsort(weights)[::-1]
        boxes = boxes[indices]
        weights = weights[indices]
        
        keep = []
        for i, box in enumerate(boxes):
            is_duplicate = False
            for j in keep:
                if self._calculate_overlap(box, boxes[j]) > overlap_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                keep.append(i)
        
        return boxes[keep].tolist(), weights[keep].tolist()
    
    def _calculate_overlap(self, box1, box2):
        """Calculate overlap ratio between two bounding boxes"""
        x1_1, y1_1, w1, h1 = box1
        x1_2, y1_2, w2, h2 = box2
        
        x2_1, y2_1 = x1_1 + w1, y1_1 + h1
        x2_2, y2_2 = x1_2 + w2, y1_2 + h2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def start_countdown(self):
        """Start the countdown timer"""
        self.countdown_start_time = time.time()
        self.countdown_active = True
        print(f"⏰ Starting {self.countdown_duration}-second countdown...")
    
    def stop_countdown(self):
        """Stop the countdown timer"""
        self.countdown_active = False
        print("⏹️ Countdown stopped")
    
    def get_countdown_remaining(self):
        """Get remaining countdown time"""
        if not self.countdown_active:
            return 0
        
        elapsed = time.time() - self.countdown_start_time
        remaining = max(0, self.countdown_duration - elapsed)
        
        if remaining <= 0:
            self.countdown_active = False
            return 0
        
        return remaining
    
    def is_countdown_finished(self):
        """Check if countdown has finished"""
        return self.countdown_active and self.get_countdown_remaining() == 0
    
    def get_latest_detection_results(self):
        """Get the latest detection results for display"""
        return self.last_detection_results.copy() if self.last_detection_results else []
    
    def draw_detections(self, frame, person_boxes, object_results):
        """Draw bounding boxes on the frame"""
        # Draw person detections in green
        for i, (x, y, w, h) in enumerate(person_boxes):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(frame, f'Person {i+1}', (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Draw object detections in different colors
        colors = [(255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]  # BGR format
        
        for result in object_results:
            boxes = result['boxes']
            scores = result['scores']
            labels = result['labels']
            
            for i, (box, score, label) in enumerate(zip(boxes, scores, labels)):
                x1, y1, x2, y2 = map(int, box)
                color = colors[i % len(colors)]
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                cv2.putText(frame, f'{label}: {score:.2f}', (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return frame
    
    def draw_status_overlay(self, frame):
        """Draw status information on the frame"""
        height, width = frame.shape[:2]
        
        # Calculate runtime
        runtime = time.time() - self.stats['start_time']
        
        # Create status text
        status_lines = [
            f"Runtime: {runtime:.1f}s",
            f"Frames: {self.stats['total_frames']}",
            f"Objects: {self.stats['objects_detected']}",
            f"Saved: {self.stats['frames_saved']}",
            f"Auto: {self.stats['auto_captures']} | Manual: {self.stats['manual_captures']}",
            f"FPS: {self.stats['total_frames']/runtime:.1f}" if runtime > 0 else "FPS: 0",
            f"Mode: Pure photo booth"
        ]
        
        # Add countdown status
        if self.countdown_active:
            remaining = self.get_countdown_remaining()
            if remaining > 0:
                status_lines.append(f"⏰ COUNTDOWN: {remaining:.1f}s")
            else:
                status_lines.append("📸 CAPTURING...")
        else:
            status_lines.append("🎯 Always-take-picture mode")
        
        # Add async detection status
        if self.detection_in_progress:
            status_lines.append("🔄 Detecting objects...")
        elif self.detection_queue.qsize() > 0:
            status_lines.append(f"⏳ Queue: {self.detection_queue.qsize()}")
        else:
            status_lines.append("✅ Detection ready")
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw status text
        for i, line in enumerate(status_lines):
            y_pos = 35 + i * 20
            cv2.putText(frame, line, (20, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw controls info
        controls_text = "Controls: 'q'=quit, 's'=save, 'c'=countdown, 'h'=help"
        cv2.putText(frame, controls_text, (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw debug status
        if self.debug_mode:
            debug_text = f"DEBUG: threshold={self.person_detection_threshold:.1f}"
            cv2.putText(frame, debug_text, (10, height - 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Draw countdown in center of screen
        if self.countdown_active:
            remaining = self.get_countdown_remaining()
            if remaining > 0:
                # Draw large countdown circle
                center_x, center_y = width // 2, height // 2
                radius = 80
                
                # Draw background circle
                cv2.circle(frame, (center_x, center_y), radius, (0, 0, 0), -1)
                cv2.circle(frame, (center_x, center_y), radius, (0, 255, 255), 5)
                
                # Draw countdown number
                countdown_text = f"{int(remaining) + 1}"
                font_scale = 3.0
                font_thickness = 8
                text_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
                text_x = center_x - text_size[0] // 2
                text_y = center_y + text_size[1] // 2
                
                cv2.putText(frame, countdown_text, (text_x, text_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 255), font_thickness)
                
                # Draw "GET READY!" text
                ready_text = "GET READY!"
                ready_size = cv2.getTextSize(ready_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                ready_x = center_x - ready_size[0] // 2
                ready_y = center_y - radius - 20
                
                cv2.putText(frame, ready_text, (ready_x, ready_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        
        return frame
    
    def save_frame(self, frame, person_boxes, object_results, use_matplotlib_viz=False, is_auto_capture=False):
        """Save frame with detections - optionally using matplotlib visualization from image_detection.py"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        
        if use_matplotlib_viz and any(len(result['boxes']) > 0 for result in object_results):
            # Use matplotlib visualization from image_detection.py
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            text_queries = self.text_queries.split('.')[:-1]  # Remove empty string from split
            
            print(f"\n💾 Saving detection with matplotlib visualization...")
            image_detection.visualize_detections(pil_image, object_results, text_queries)
            
            # Also save the OpenCV version
            frame_with_detections = frame.copy()
            frame_with_detections = self.draw_detections(frame_with_detections, person_boxes, object_results)
            frame_with_detections = self.draw_status_overlay(frame_with_detections)
            
            filename = f"{self.output_dir}/detection_{timestamp}.jpg"
            cv2.imwrite(filename, frame_with_detections)
        else:
            # Use original OpenCV visualization
            frame_with_detections = frame.copy()
            frame_with_detections = self.draw_detections(frame_with_detections, person_boxes, object_results)
            frame_with_detections = self.draw_status_overlay(frame_with_detections)
            
            # Save the frame
            filename = f"{self.output_dir}/detection_{timestamp}.jpg"
            cv2.imwrite(filename, frame_with_detections)
        
        self.stats['frames_saved'] += 1
        
        # Track auto vs manual captures
        if is_auto_capture:
            self.stats['auto_captures'] += 1
            capture_type = "AUTO"
        else:
            self.stats['manual_captures'] += 1
            capture_type = "MANUAL"
        
        # Print detection summary
        print(f"\n💾 Detection saved ({capture_type}): {filename}")
        print(f"   👤 Persons detected: {len(person_boxes)}")
        
        total_objects = 0
        for result in object_results:
            if len(result['boxes']) > 0:
                total_objects += len(result['boxes'])
                print(f"   🎯 Objects detected:")
                for box, score, label in zip(result['boxes'], result['scores'], result['labels']):
                    print(f"     - {label}: {score:.3f} confidence")
        
        if total_objects == 0:
            print(f"   ❌ No objects detected")
        
        print(f"   📊 Total saved frames: {self.stats['frames_saved']}")
        print(f"   📸 Auto captures: {self.stats['auto_captures']} | Manual captures: {self.stats['manual_captures']}")
        print("-" * 50)
        
        return filename
    
    def print_help(self):
        """Print help information"""
        print("\n" + "="*60)
        print("🎮 LIVE OBJECT DETECTION - CONTROLS")
        print("="*60)
        print("📹 Camera Controls:")
        print("   'q' or ESC - Quit the application")
        print("   's' - Save current frame manually")
        print("   'm' - Save with matplotlib visualization (from image_detection.py)")
        print("   'c' - Start countdown timer manually")
        print("   'x' - Stop countdown timer")
        print("   'h' - Show this help")
        print("   'r' - Reset statistics")
        print("   't' - Toggle detection threshold")
        print("   'd' - Toggle debug mode")
        print("   'v' - Toggle verbose detection")
        print("\n🎯 Detection Info:")
        print(f"   Person threshold: {self.person_detection_threshold}")
        print(f"   Object threshold: {self.object_detection_threshold}")
        print(f"   Detection targets: {self.text_queries}")
        print(f"   Countdown duration: {self.countdown_duration} seconds")
        print(f"   Output directory: {self.output_dir}")
        print("\n📸 Photo Booth Mode:")
        print("   Pure photo booth - no person detection required")
        print("   Press 'c' to start 5-second countdown")
        print("   After countdown, a picture is ALWAYS taken")
        print("   Press 'x' to stop countdown manually")
        print("\n🎯 Object Detection:")
        print("   Detects masks, gloves, and hairnets in photos")
        print("   Detection runs in background without blocking video")
        print("="*60)
    
    def run_live_detection(self, camera_index=0):
        """Main function to run live detection"""
        print("\n🎬 Starting Live Object Detection...")
        print("📋 Press 'h' for help and controls")
        print("=" * 60)
        
        # Initialize camera
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Error: Could not open camera {camera_index}")
            print("💡 Try different camera indices: 0, 1, 2...")
            print("💡 Or check camera permissions in System Preferences")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("✅ Camera initialized successfully!")
        print(f"📐 Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        print(f"🎞️  FPS: {cap.get(cv2.CAP_PROP_FPS)}")
        print("=" * 60)
        
        frame_count = 0
        last_status_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Error: Could not read frame")
                    break
                
                frame_count += 1
                self.stats['total_frames'] = frame_count
                
                # Check if countdown has finished (manual countdown only)
                if self.countdown_active and self.is_countdown_finished():
                    print(f"📸 Countdown finished! Taking picture...")
                    print(f"🔍 Queuing frame for async detection...")
                    
                    # Queue frame for async object detection
                    if self.queue_detection(frame):
                        print("🔄 Object detection queued for captured frame...")
                    
                    # Use last detection results if available, otherwise empty results
                    object_results = self.last_detection_results if self.last_detection_results else []
                    
                    # Always save the frame (no person detection needed)
                    self.save_frame(frame, [], object_results, is_auto_capture=False)
                    self.last_detection_time = time.time()
                    
                    # Draw object detections on frame
                    frame = self.draw_detections(frame, [], object_results)
                
                # Always draw latest detection results if available
                if not self.countdown_active and len(self.get_latest_detection_results()) > 0:
                    latest_results = self.get_latest_detection_results()
                    frame = self.draw_detections(frame, [], latest_results)
                
                # Add status overlay
                frame = self.draw_status_overlay(frame)
                
                # Display the frame
                cv2.imshow('Live Object Detection', frame)
                
                # Print periodic status updates
                if time.time() - last_status_time > 10:  # Every 10 seconds
                    runtime = time.time() - self.stats['start_time']
                    fps = frame_count / runtime if runtime > 0 else 0
                    print(f"📊 Status: {frame_count} frames, {fps:.1f} FPS, {self.stats['persons_detected']} persons, {self.stats['objects_detected']} objects")
                    last_status_time = time.time()
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                elif key == ord('s'):
                    # Manual save - always works
                    print("📸 Manual save triggered, queuing async detection...")
                    # Queue frame for async detection
                    if self.queue_detection(frame):
                        print("🔄 Object detection queued...")
                    # Use last detection results if available
                    object_results = self.last_detection_results if self.last_detection_results else []
                    self.save_frame(frame, [], object_results, is_auto_capture=False)
                elif key == ord('m'):
                    # Manual save with matplotlib visualization - always works
                    print("📸 Manual matplotlib save triggered, queuing async detection...")
                    # Queue frame for async detection
                    if self.queue_detection(frame):
                        print("🔄 Object detection queued...")
                    # Use last detection results if available
                    object_results = self.last_detection_results if self.last_detection_results else []
                    self.save_frame(frame, [], object_results, use_matplotlib_viz=True, is_auto_capture=False)
                elif key == ord('c'):
                    # Start countdown manually
                    if not self.countdown_active:
                        self.start_countdown()
                    else:
                        print("⏰ Countdown already active!")
                elif key == ord('x'):
                    # Stop countdown manually
                    if self.countdown_active:
                        self.stop_countdown()
                    else:
                        print("⏹️ No countdown active!")
                elif key == ord('h'):
                    self.print_help()
                elif key == ord('r'):
                    # Reset statistics
                    self.stats = {
                        'total_frames': frame_count,
                        'objects_detected': 0,
                        'frames_saved': 0,
                        'auto_captures': 0,
                        'manual_captures': 0,
                        'start_time': time.time()
                    }
                    print("🔄 Statistics reset!")
                elif key == ord('t'):
                    # Toggle detection threshold
                    self.person_detection_threshold = 0.3 if self.person_detection_threshold > 0.5 else 0.7
                    print(f"🎚️  Person detection threshold: {self.person_detection_threshold}")
                elif key == ord('d'):
                    # Toggle debug mode
                    self.debug_mode = not self.debug_mode
                    self.show_detection_attempts = self.debug_mode
                    print(f"🐛 Debug mode: {'ON' if self.debug_mode else 'OFF'}")
                elif key == ord('v'):
                    # Toggle verbose detection attempts
                    self.show_detection_attempts = not self.show_detection_attempts
                    print(f"📢 Verbose detection: {'ON' if self.show_detection_attempts else 'OFF'}")
        
        except KeyboardInterrupt:
            print("\n⏹️  Detection stopped by user")
        
        finally:
            # Stop async detection thread
            self.stop_async_detection()
            
            cap.release()
            cv2.destroyAllWindows()
            
            # Print final statistics
            runtime = time.time() - self.stats['start_time']
            print("\n" + "="*60)
            print("📊 FINAL STATISTICS")
            print("="*60)
            print(f"⏱️  Total runtime: {runtime:.1f} seconds")
            print(f"🎞️  Total frames: {self.stats['total_frames']}")
            print(f"📈 Average FPS: {self.stats['total_frames']/runtime:.1f}")
            print(f"🎯 Objects detected: {self.stats['objects_detected']}")
            print(f"💾 Frames saved: {self.stats['frames_saved']}")
            print(f"📸 Auto captures: {self.stats['auto_captures']}")
            print(f"📸 Manual captures: {self.stats['manual_captures']}")
            print(f"📁 Output directory: {self.output_dir}")
            print("="*60)
            print("✅ Photo booth session completed!")

def main():
    detector = LiveObjectDetector()
    
    # Try different camera indices if needed
    camera_index = 0
    detector.run_live_detection(camera_index)

if __name__ == "__main__":
    main()
