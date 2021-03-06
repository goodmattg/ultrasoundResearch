import argparse
import cv2
import json
import os

import matplotlib.pyplot as plt
import numpy as np

from src.utilities.segmentation.xianauto.automatic import get_ROI_debug

from src.constants.ultrasound import HSV_COLOR_THRESHOLD
from src.constants.ultrasound import (
    IMAGE_TYPE,
    IMAGE_TYPE_LABEL,
    FRAME_LABEL,
    FRAME_DEFAULT_ROW_CROP_FOR_SCAN_SELECTION,
    FRAME_DEFAULT_COL_CROP_FOR_SCAN_SELECTION)

from src.utilities.segmentation.brute.grayscale import select_scan_window_from_frame
from src.pipeline.patientsample.patient_sample_generator import PatientSampleGenerator


def __select_random_grayscale_frame(patient_frames_path, manifest, patient):
    gf = [fr[FRAME_LABEL] for fr in manifest[patient]
          if fr[IMAGE_TYPE_LABEL] == IMAGE_TYPE.GRAYSCALE.value]
    return os.path.join(patient_frames_path, np.random.choice(gf))


def __is_frame_clear(self, frame):
    return frame[IMAGE_TYPE_LABEL] == self.image_type.value


def __get_random_frames(
    benign_top_level_path,
    malignant_top_level_path,
    manifest_path,
    frame_folder,
    number_frames=3):

    dirname = os.path.dirname(__file__)

    with open(manifest_path, "r") as fp:
        manifest = json.load(fp)

    mpat = [name for name in os.listdir(malignant_top_level_path)
            if os.path.isdir(os.path.join(malignant_top_level_path, name))]

    bpat = [name for name in os.listdir(benign_top_level_path)
            if os.path.isdir(os.path.join(benign_top_level_path, name))]

    num_malignant = number_frames // 2
    num_benign = number_frames - num_malignant

    # Sample the patients 
    mpat_bar = [(p, "MALIGNANT") for p in np.random.choice(mpat, num_malignant)]
    bpat_bar = [(p, "BENIGN") for p in np.random.choice(bpat, num_benign)]

    # From each patient, randomly grab one grayscale frame
    mpat_frames = [
        (p, __select_random_grayscale_frame(os.path.join(
            malignant_top_level_path, p, frame_folder), manifest, p), tag)
        for (p, tag) in mpat_bar]

    bpat_frames = [
        (p, __select_random_grayscale_frame(os.path.join(
            benign_top_level_path, p, frame_folder), manifest, p), tag)
        for (p, tag) in bpat_bar]

    return mpat_frames + bpat_frames


def __grayscale_region_of_interest_graphic(
        benign_top_level_path,
        malignant_top_level_path,
        manifest_path,
        frame_folder,
        rows=1,
        cols=3):

    # Get random frames from the entire set of patients
    random_frames = __get_random_frames(
        benign_top_level_path,
        malignant_top_level_path,
        manifest_path,
        frame_folder,
        number_frames=(rows * cols))

    # Display the randomly chosen frame
    for p, f, label in random_frames:

        image = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
        M, N = image.shape

        # Get the scan window
        scan_window, scan_bounds = select_scan_window_from_frame(
            image, 
            5, 255, 
            select_bounds = (
                slice(FRAME_DEFAULT_ROW_CROP_FOR_SCAN_SELECTION, M), 
                slice(FRAME_DEFAULT_COL_CROP_FOR_SCAN_SELECTION, N)))

        # Destructure the scan window bounds
        x_s, y_s, w_s, h_s = scan_bounds

        # Run Xian automatic segmentation to get ROI
        roi_rect, seed_pt = get_ROI_debug(scan_window)
        x_r, y_r, w_r, h_r = roi_rect

        color_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        # Draw the rectangle of the scan window onto the original frame
        cv2.rectangle(
            color_image,
            (x_s, y_s),
            (x_s + w_s, y_s + h_s),
            (0, 0, 255),
            2)

        # Draw the ROI rectangle
        cv2.rectangle(
            color_image,
            (x_r + x_s, y_r + y_s),
            (x_r + x_s + w_r, y_r + y_s + h_r),
            (0, 255, 0),
            2)

        # Draw the seed point of the tumor ROI
        cv2.circle(
            color_image, 
            (
                x_s + int(seed_pt[1]), 
                y_s + int(seed_pt[0])
            ), 
            5, 
            (255, 0, 0), -1)
        
        cv2.imshow("Patient: {} | Type: {}".format(p, label), color_image)
        cv2.waitKey(0)
