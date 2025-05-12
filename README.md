# Event and Image Extraction from ROS Bag

## Overview

`event_image_extractor.py` is a Python script that processes a ROS bag recording from a Prophesee EVK4 event camera and a peak CMOS image sensor. It extracts:

- **Event data** from `/prophesee/camera/cd_events_buffer` topic into a text file
- **Decoded image frames** from `/peak_cam_node/image_raw` topic into a sequence of PNG files
- **Timestamps** for each saved image into a separate log file

Extraction begins at a configurable offset relative to the first image timestamp and stops when a maximum file size limit is reached.

## Features

- **Dual-topic extraction**: Handles both event streams and image messages in one pass.
- **Timestamp-based filtering**: Starts saving events only once the time exceeds `first_image_ts - offset_us`.
- **Automatic directory creation**: Creates an output folder for images if it doesn’t exist.
- **File size guard**: Stops processing when the event file exceeds the defined maximum size.
- **Buffered writes**: Flushes event data periodically for reliability.

## Prerequisites

- **ROS Noetic** (or compatible) with `rosbag` Python API
- **Prophesee ROS driver** and its message definitions (`prophesee_event_msgs/msg/EventArray`)
- **OpenCV** and `cv_bridge` for image conversion
- **Python packages**:
  - `rosbag`
  - `rospy`
  - `cv2` (OpenCV)
  - `cv_bridge`
  - `os`, `sys`, `threading`, `time`

## Configuration

Edit the following variables at the top of the script:

| Variable               | Description                                        | Example Value                                      |
|------------------------|----------------------------------------------------|----------------------------------------------------|
| `bag_path`             | Path to input ROS bag file                         | `/home/user/recordings/2025-05-01-16-38-16.bag`     |
| `output_event_file`    | Path to output text file for events                | `/home/user/outputs/events_seq_3.txt`              |
| `image_output_dir`     | Directory to save extracted images                 | `/home/user/outputs/extracted_images_seq3`         |
| `timestamp_log_file`   | File logging image filenames with timestamps       | `/home/user/outputs/image_timestamps_seq3.txt`     |
| `max_file_size`        | Maximum bytes for event file before stopping       | `9 * 1024 * 1024 * 1024` (9 GB)                    |
| `offset_us`            | Microseconds to subtract from first image timestamp| `11111`                                            |

## Installation

1. **Ensure ROS dependencies**:
   ```bash
   sudo apt-get install ros-noetic-rosbag ros-noetic-cv-bridge python3-opencv

    Place script in your ROS workspace or project folder.

    Install Python requirements (if using pip):

    pip install opencv-python

Usage

Run the script directly with Python:

python3 event_image_extractor.py

Monitor the console for info messages:

    First image timestamp

    When event saving starts

    Warnings upon reaching file-size limit

    Final counts of saved images and events

How It Works

    Read Bag: Opens the ROS bag and reads the first image from /peak_cam_node/image_raw to determine first_image_ts_us.

    Compute Offset: Calculates start_event_ts_us = first_image_ts_us - offset_us.

    Reopen Bag: Iterates through both topics:

        Image Messages: Converts and saves each image via CvBridge → PNG. Logs filename + timestamp.

        Event Messages: For each event, checks if event.ts >= start_event_ts_us; if so, writes [ts, x, y, polarity] to the event text file.

    Termination: Continues until bag end or event file exceeds max_file_size.

Troubleshooting

    Missing Topics: Verify topic names in the bag with:

    rosbag info /path/to/bag.bag

    CV Bridge Errors: Ensure matching ROS Python environment and correct OpenCV version.

    Large Files: Adjust max_file_size or split processing into smaller segments.

    Permission Denied: Check write permissions on output directories.

License

This script is released under the MIT License. See LICENSE for details.
Author

Shahid Shabeer Malik – Graduate Research Assistant, SLUAIR Lab, Saint Louis University

Contact: shahid.malik@slu.edu
