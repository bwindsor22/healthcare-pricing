from pathlib import Path
import camelot
import math
from typing import Tuple, Union

import cv2
import numpy as np

from deskew import determine_skew

resources = Path('/Users/bradwindsor/classwork/nlphealthcare/final-proj/resources/')

def rotate(
        image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]
) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)




def run_deskew(in_path, in_path2):
    image = cv2.imread(in_path)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    angle = determine_skew(grayscale)
    angle2 = getSkewAngle(grayscale)
    if angle:
        rotated = rotate(image, angle, (0, 0, 0))
        cv2.imwrite(in_path2, rotated)
    else:
        cv2.imwrite(in_path2, image)

def getSkewAngle(gray) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    # newImage = cvImage.copy()
    # gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=5)

    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    minAreaRect = cv2.minAreaRect(largestContour)

    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle


def run_tesseract(in_path2, out_path):
    try:
        from PIL import Image
    except ImportError:
        import Image
    import pytesseract

    # If you don't have tesseract executable in your PATH, include the following:
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
    # Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

    # Simple image to string
    # print(pytesseract.image_to_data(Image.open(in_path)))
    pdf = pytesseract.image_to_pdf_or_hocr(in_path2, extension='pdf')
    with open(out_path, 'w+b') as f:
        f.write(pdf) # pdf type is bytes by default
    try:
        tables = camelot.read_pdf(out_path, flavor='stream')
        dfs = [t.df for t in tables]
        return dfs
    except Exception:
        return []

def load_imgs_as_dfs():
    sources = resources / 'bills'
    dfs = dict()
    for file in sources.glob('*.png'):
        in_path = str(file)
        deskewed_path = file.parent.parent / 'img_deskew' / file.name
        out_path = file.parent.parent / 'pdf' / (file.stem + '.pdf')
        run_deskew(in_path, deskewed_path.as_posix())
        img_dfs = run_tesseract(deskewed_path.as_posix(), out_path.as_posix())
        dfs[file.stem] = img_dfs

    # best are img_1
    # single offset: img_12
    # slightly worse: img6
    return dfs
    print('hi')


load_imgs_as_dfs()