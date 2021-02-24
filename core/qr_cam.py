import asyncio
from typing import Any, Tuple

import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
from loguru import logger
from PIL import Image, ImageDraw, ImageFont

from core.config import args
from handlers import notify


cap = cv2.VideoCapture(0)


def create_square(frame: Any, side: int = 240) -> np.array:
    """Calculates the (x,y)-coordinates of the centered square of side :side: for the captured frame.

    Args:
        frame (Union[Mat, UMat]): A frame of the webcam's captured stream.
        [optional] side (int): Length of the side of a square to be drawn in the center of the screen.

    Raises:
        ValueError: On invalid length of the square. Its side can't be less of 10 and more than the minimum of height
        and width of the frame.  It can't fit in the frame.

    Returns:
        square (np.ndarray): A numpy array of the square's (x,y)-coordinates on the frame.
    """

    height, width = np.size(frame, 0), np.size(frame, 1)
    image_center = (width // 2, height // 2)

    if side > min(width, height):
        raise ValueError(
            "Invalid length of a square. Can't be more than %d.\n"
            "Web-cam connection has been aborted, the bot is still running. "
            'Press "CTRL+C" to shutdown the bot completely' % min(width, height)
        )

    tl = (image_center[0] - (side // 2), image_center[1] - (side // 2))
    tr = (image_center[0] + (side // 2), image_center[1] - (side // 2))
    bl = (image_center[0] - (side // 2), image_center[1] + (side // 2))
    br = (image_center[0] + (side // 2), image_center[1] + (side // 2))
    points = [tl, tr, br, bl]
    square = np.array(points, dtype="int0")

    return square


def draw_bounds(
    frame: Any,
    square: np.ndarray,
    length_lines: int = 10,
    color_lines: Tuple[int, ...] = (240, 240, 240),
    lang: str = "en",
    color_text: Tuple[int, ...] = (240, 240, 240),
):
    """Draws a square-shaped overlay on the frame to indicate where to fit a QR-code in.
    Also adds some pretty corners and an explanation.

    Args:
        frame (Union[Mat, UMat]): A frame of the webcam's captured stream.
        square (np.ndarray): A numpy array of the square's (x,y)-coordinates on the frame.
        [optional] lenght_lines (int): Pretty corners' lines length.
        [optional] color_lines (tuple): Pretty corners' lines color.
        [optional] lang (str): A language of the explanation's text ("en" or "ru").
        [optional] color_text (tuple): The explanation's text color.

    Returns:
        image (Union[Mat, UMat]): An image with the square-shaped overlay, pretty corners and explanation.
    """

    image = frame.copy()
    black_screen = np.zeros(frame.shape, dtype="uint8")
    image = cv2.addWeighted(image, 0.55, black_screen, 0.45, 1.0)
    cropped = frame[square[0][1] : square[2][1], square[0][0] : square[2][0]]
    image[square[0][1] : square[2][1], square[0][0] : square[2][0]] = cropped

    cv2.line(
        image,
        (square[0][0], square[0][1]),
        (square[0][0] + length_lines, square[0][1]),
        color_lines,
        2,
        lineType=cv2.LINE_AA,
    )
    cv2.line(
        image,
        (square[0][0], square[0][1]),
        (square[0][0], square[0][1] + length_lines),
        color_lines,
        2,
        lineType=cv2.LINE_AA,
    )

    cv2.line(
        image,
        (square[1][0], square[1][1]),
        (square[1][0] - length_lines, square[1][1]),
        color_lines,
        2,
        lineType=cv2.LINE_AA,
    )
    cv2.line(
        image,
        (square[1][0], square[1][1]),
        (square[1][0], square[1][1] + length_lines),
        color_lines,
        2,
        lineType=cv2.LINE_AA,
    )

    cv2.line(
        image,
        (square[2][0], square[2][1]),
        (square[2][0] - length_lines, square[2][1]),
        color_lines,
        2,
        lineType=cv2.LINE_AA,
    )
    cv2.line(
        image,
        (square[2][0], square[2][1]),
        (square[2][0], square[2][1] - length_lines),
        color_lines,
        2,
        lineType=cv2.LINE_AA,
    )

    cv2.line(
        image,
        (square[3][0], square[3][1]),
        (square[3][0] + length_lines, square[3][1]),
        color_lines,
        2,
        lineType=cv2.LINE_AA,
    )
    cv2.line(
        image,
        (square[3][0], square[3][1]),
        (square[3][0], square[3][1] - length_lines),
        color_lines,
        2,
        lineType=cv2.LINE_AA,
    )

    if lang == "ru":
        image_pil = Image.fromarray(image)
        font = ImageFont.truetype("arial.ttf", 14)
        color_text += (1,)
        draw = ImageDraw.Draw(image_pil)

        text = "Поместите Ваш QR-код в квадрат"
        text_xy = (208, square[0][1] - 24)
        draw.text(text_xy, text, font=font, fill=color_text)
        image = np.array(image_pil)

    else:
        text = "Fit your QR-code inside the square"
        text_xy = (180, square[0][1] - 10)
        cv2.putText(
            image,
            text,
            text_xy,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color_text,
            lineType=cv2.LINE_AA,
        )

    return image


def order_points(points: np.ndarray) -> np.ndarray:
    """Sorts a rectangle's points from top-left to bottom-left, so the points array has the following order:
    0   1
    3   2

    Args:
        points (np.ndarray): A numpy array of a rectangle's (x,y)-coordinates.

    Returns:
        rect (np.ndarray): The ordered numpy array of the rectangle's coordinates.
    """

    rect = np.zeros((4, 2), dtype="int0")

    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]
    rect[2] = points[np.argmax(s)]

    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]
    rect[3] = points[np.argmax(diff)]

    return rect


def contains_in_area(rectangle: np.ndarray, square: np.ndarray) -> bool:
    """Checks whether a rectangle fully contains inside the area of a square.

    Args:
        rectangle (np.array): An ordered numpy array of a rectangle's coordinates.
        square (np.array): An ordered numpy array of a square's coordinates.

    Returns:
        Whether the rectangle contains inside the square.  Since the both arrays are ordered it's suffice
        to check that the top-left and the bottom-right points of the rectangle are both in the square.
    """

    if ((rectangle[0][0] < square[0][0]) or (rectangle[0][1] < square[0][1])) or (
        (rectangle[2][0] > square[2][0]) or (rectangle[2][1] > square[2][1])
    ):
        return False

    return True


def detect_inside_square(
    frame: Any,
    square: np.ndarray,
    kernel: np.ndarray,
    area_min: int = 300,
    color_lower: int = 212,
    color_upper: int = 255,
    debug: bool = False,
) -> Tuple[bool, Any]:
    """Detects and analyzes contours and shapes on the frame.  If the detected shape's area is >= :area_min:,
    its color hue is >= :color_lower and a rectangle that encloses the shape contains inside the square returns True
    and the cropped image of the frame.

    Args:
        frame (Union[Mat, UMat]): A frame of the webcam's captured stream.
        square (np.ndarray): A numpy array of the square's (x,y)-coordinates on the frame.
        kernel (np.ndarray): A kernel for the frame dilation and transformation (to detect the contours of shapes).
        [optional] area_min (int): Minimal area of a detected object to be consider a QR-code.
        [optional] color_lower (int): Minimal hue of gray of a detected object to be consider a QR-code.
        [optional] color_upper (int): Maximal hue of gray of a detected object to be consider a QR-code.
        [optional] debug (boolean): Crops and outputs an image containing inside the square at potential detection.

    Returns:
        A tuple where the first element is whether a potential shape has been detected inside the square or not.
        If it was then the second element is the square-cropped image with the detected shape, None otherwise.
    """

    filter_lower = np.array(color_lower, dtype="uint8")
    filter_upper = np.array(color_upper, dtype="uint8")
    mask = cv2.inRange(frame, filter_lower, filter_upper)
    dilation = cv2.dilate(mask, kernel, iterations=3)
    closing = cv2.morphologyEx(dilation, cv2.MORPH_GRADIENT, kernel)
    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel)
    closing = cv2.GaussianBlur(closing, (3, 3), 0)
    edge = cv2.Canny(closing, 175, 250)

    contours, hierarchy = cv2.findContours(edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < area_min:
            continue

        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        rect = order_points(box)
        cv2.drawContours(frame, [box], 0, (0, 0, 255), 1)

        if not contains_in_area(rect, square):
            continue

        cropped = frame[square[0][1] : square[2][1], square[0][0] : square[2][0]]

        if debug:
            cv2.imshow("Edges", edge)
            cv2.imshow("Cropped", cropped)

        return (True, cropped)

    return (False, None)


def detect_qr(image: Any) -> str:
    """Tries to locate and decode one (or multiple) QR-codes from :image:.

    Args:
        image (Union[Mat, UMat]): A square crop of a frame from the web-cam's stream.

    Returns:
        A decoded str of the first located QR-code. None if a QR-code can't be located.
    """

    img = image.copy()
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    codes = pyzbar.decode(img_gray)

    if not codes:
        return ""

    if len(codes) > 1:
        logger.warning("Multiple QR-codes has been detected in the frame. Selecting the first one")

        for decoded in codes:
            points = np.array(decoded.polygon, np.int32)
            points = points.reshape((-1, 1, 2))
            cv2.polylines(image, [points], True, (196, 0, 0), 3)

    result = codes[0].data.decode("utf-8")
    return result


async def scan_qr() -> None:
    """Main function that creates a screen with the capture, monitors the web-cam's stream, searches for a QR-code in
    a squared area and passes the decoded QR-code to the notify module.
    All required arguments are defined in the Argparse Namespace that's set in config.py/args, hence, no arguments in
    this coroutine function.
    """

    if (cap is None) or (not cap.isOpened()):
        logger.critical("No video stream detected. Make sure that you've got a webcam connected and enabled")
        return

    kernel = np.ones((2, 2), np.uint8)
    square = create_square(cap.read()[1], side=args.side)

    while cap.isOpened():
        ret, frame = cap.read()
        key = cv2.waitKey(1)

        if not ret or square is None or ((key & 0xFF) in {27, ord("Q"), ord("q")}):
            free_all()
            logger.info(
                'Web-cam has been shut down, the bot is still running. Press "CTRL+C" to shutdown the bot completely'
            )
            return

        image = draw_bounds(frame, square, lang=args.lang)
        cv2.imshow("Live Capture", image)
        await asyncio.sleep(0.1)

        detected, cropped = detect_inside_square(
            frame, square, kernel, area_min=args.area, color_lower=args.color, debug=args.verbose
        )

        if not detected:
            continue

        address = detect_qr(cropped)

        if not address:
            continue

        logger.debug('Detected: "{}"', address)
        await notify.start(address, args.pause)


def free_all() -> None:
    """Releases the web-cam capture."""

    cv2.destroyAllWindows()
    cap.release()
