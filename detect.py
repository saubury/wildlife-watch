import argparse
import sys
import time
import cv2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
import utils
import json 
from collections import Counter
from confluent_kafka import Producer
import configparser

config_file_name = 'ww.ini'

      
# Continuously run inference on images acquired from the camera
def run(model: str, camera_id: int, width: int, height: int, num_threads: int,
        kafka_producer, videoFile, hide_preview, config) -> None:

  # Variables to calculate FPS
  counter, fps = 0, 0
  start_time = time.time()

  if videoFile:
    # Video file was specified
    cap = cv2.VideoCapture(videoFile)
  else:
    # Start capturing video input from the camera
    cap = cv2.VideoCapture(camera_id)
    
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

  # Visualization parameters
  row_size = 20  # pixels
  left_margin = 24  # pixels
  text_color = (0, 0, 255)  # red
  font_size = 1
  font_thickness = 1
  fps_avg_frame_count = 10

  # Initialize the object detection model
  base_options = core.BaseOptions(file_name=model, num_threads=num_threads)
  detection_options = processor.DetectionOptions(max_results=3, score_threshold=0.3)
  options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
  detector = vision.ObjectDetector.create_from_options(options)

  # Continuously capture images from the camera and run inference
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      sys.exit(
          'ERROR: Unable to read from webcam. Please verify your webcam settings.'
      )

    counter += 1
    image = cv2.flip(image, 1)

    # Convert the image from BGR to RGB as required by the TFLite model.
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Create a TensorImage object from the RGB image.
    input_tensor = vision.TensorImage.create_from_array(rgb_image)

    # Run object detection estimation using the model.
    detection_result = detector.detect(input_tensor)

    detection_result_dict = dumpDetect(detection_result)
    detection_result_count = Counter(k['class_name'] for k in detection_result_dict if k.get('class_name'))


    json_payload = {
      "camera_name": config['common']['camera.name'],
      "objects_found": detection_result_dict,
      "objects_count": detection_result_count
    }
    json_dump = json.dumps(json_payload)
    print(json_dump)
    
    if not kafka_producer:
      print('Sending stuff to Kafka')
      kafka_producer.poll(0)
      kafka_producer.produce(config['kafka']['topic'], json_dump.encode('utf-8'), callback=delivery_report)
      kafka_producer.flush()

    # Calculate the FPS
    if counter % fps_avg_frame_count == 0:
      end_time = time.time()
      fps = fps_avg_frame_count / (end_time - start_time)
      start_time = time.time()

    # Show the FPS
    fps_text = 'FPS = {:.1f}'.format(fps)
    text_location = (left_margin, row_size)

    # Draw keypoints and edges on input image
    image = utils.visualize(image, detection_result)
    cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                font_size, text_color, font_thickness)

    # Stop the program if the ESC key is pressed.
    if cv2.waitKey(1) == 27:
      break

    if not hide_preview:
      cv2.imshow('object_detector', image)

  cap.release()
  cv2.destroyAllWindows()
  # end of run





def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))


def dumpDetect(detection_result: processor.DetectionResult):
  return_dict = []

  for detection in detection_result.detections:
    category = detection.classes[0]
    class_name = category.class_name
    probability = round(category.score, 2)
    return_dict.append({'class_name':class_name, 'probability':probability})

  return return_dict

def main():
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model',
      help='Path of the object detection model.',
      required=False,
      default='efficientdet_lite0.tflite')
  parser.add_argument(
      '--videoFile',
      help='Path of the video file (.mp4) to be used instead of live camera capture.',
      required=False)      
  parser.add_argument(
      '--cameraId', help='Id of camera.', required=False, type=int, default=0)
  parser.add_argument(
      '--frameWidth',
      help='Width of frame to capture from camera.',
      required=False,
      type=int,
      default=640)
  parser.add_argument(
      '--frameHeight',
      help='Height of frame to capture from camera.',
      required=False,
      type=int,
      default=480)
  parser.add_argument(
      '--numThreads',
      help='Number of CPU threads to run the model.',
      required=False,
      type=int,
      default=4)
  parser.add_argument(
      '--enableKafka',
      help='Whether to enable Kafka producer.',
      action='store_true',
      required=False,
      default=False)
  parser.add_argument(
      '--hidePreview',
      help='Whether to hide preview window.',
      action='store_true',
      required=False,
      default=False)      
  args = parser.parse_args()


  config = configparser.ConfigParser()
  config.read(config_file_name)

  kafka_producer = True
  if args.enableKafka:
    print('Enabling Kafka Producer')
    kafka_producer = Producer({'bootstrap.servers': config['kafka']['bootstrap.servers']})


  run(args.model, int(args.cameraId), args.frameWidth, args.frameHeight,
      int(args.numThreads), kafka_producer, args.videoFile, args.hidePreview, config)


if __name__ == '__main__':
  main()
