# import rosbag
# from prophesee_event_msgs.msg import EventArray
# import os

# bag = rosbag.Bag('/home/lab_user/Arduino/2025-03-25-15-26-42.bag')

# # Define the maximum file size in bytes (2 GB = 2 * 1024 * 1024 * 1024 bytes)
# max_file_size = 4 * 1024 * 1024 * 1024

# output_file_path = '/home/lab_user/Arduino/2025-03-25-15-26-42.txt'

# # Open a text file for writing the output
# with open(output_file_path, 'w') as f:
#     # Read messages from the correct topic
#     for topic, msg, t in bag.read_messages(topics=['/prophesee/camera/cd_events_buffer']):
#         for event in msg.events:
#             # Convert polarity to 1 or 0
#             polarity_value = 1 if event.polarity else 0
#             #timestamp_microseconds = (t.secs * 1000000) + (t.nsecs // 1000)
#             #timestamp_microseconds = t.secs
#             event_data = f"{int(event.ts.to_sec() * 1e6)} {event.x} {event.y} {polarity_value}\n"
#             # Write to the file
#             f.write(event_data)
#             # Flush the buffer to ensure it's written to the file
#             f.flush()
#             # Check the file size after writing
#             if os.path.getsize(output_file_path) >= max_file_size:
#                 print("File size limit reached (2 GB). Stopping.")
#                 # Close the bag properly
#                 bag.close()
#                 # Close the file properly
#                 f.close()
#                 exit(0)

# bag.close()

# Input bag file
import rosbag
from prophesee_event_msgs.msg import EventArray
from sensor_msgs.msg import Image
import os
import cv2
from cv_bridge import CvBridge

bag_path = '/home/lab_user/event_extractor/scripts/2025-05-01-16-38-16.bag'
output_event_file = '/home/lab_user/Arduino/events_seq_3.txt'
image_output_dir = '/home/lab_user/Arduino/extracted_images_seq3'
timestamp_log_file = '/home/lab_user/Arduino/image_timestamps_seq3.txt'

os.makedirs(image_output_dir, exist_ok=True)
max_file_size = 9 * 1024 * 1024 * 1024
bridge = CvBridge()

# Get first image timestamp
bag = rosbag.Bag(bag_path)
first_image_ts_us = None
for topic, msg, t in bag.read_messages(topics=['/peak_cam_node/image_raw']):
    first_image_ts_us = int(msg.header.stamp.to_sec() * 1e6)
    print(f"[INFO] First image timestamp: {first_image_ts_us}")
    break
bag.close()

if first_image_ts_us is None:
    print("[ERROR] No image found in bag.")
    exit(1)

start_event_ts_us = first_image_ts_us - 11111
print(f"[INFO] Skipping events before: {start_event_ts_us} µs")

# Begin final extraction
event_count = 0
image_count = 0
saving_events = False

bag = rosbag.Bag(bag_path)
with open(output_event_file, 'w') as f_event, open(timestamp_log_file, 'w') as f_ts:
    for topic, msg, t in bag.read_messages(topics=['/prophesee/camera/cd_events_buffer', '/peak_cam_node/image_raw']):
        if topic == '/peak_cam_node/image_raw':
            try:
                cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                filename = f"frame_{image_count:06d}.png"
                filepath = os.path.join(image_output_dir, filename)
                cv2.imwrite(filepath, cv_image)

                timestamp_us = int(msg.header.stamp.to_sec() * 1e6)
                f_ts.write(f"{filename} {timestamp_us}\n")
                image_count += 1
            except Exception as e:
                print(f"[ERROR] Image conversion failed: {e}")

        elif topic == '/prophesee/camera/cd_events_buffer':
            for event in msg.events:
                ts_us = int(event.ts.to_sec() * 1e6)
                if not saving_events and ts_us >= start_event_ts_us:
                    saving_events = True
                    print(f"[INFO] Started saving events at {ts_us} µs")

                if saving_events:
                    polarity_value = 1 if event.polarity else 0
                    f_event.write(f"{ts_us} {event.x} {event.y} {polarity_value}\n")
                    event_count += 1

                    if event_count % 10000 == 0:
                        f_event.flush()

                    if os.path.getsize(output_event_file) >= max_file_size:
                        print("[WARNING] Event file size limit reached. Stopping.")
                        bag.close()
                        exit(0)
   
bag.close()
print(f"[DONE] Saved {image_count} images and {event_count} events.")
