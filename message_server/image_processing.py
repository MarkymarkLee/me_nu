import cv2
import numpy as np


def process_qr_code_image(raw_image):

    nparr = np.frombuffer(raw_image, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    qrcode = cv2.QRCodeDetector()
    data, bbox, _ = qrcode.detectAndDecode(image)

    if bbox is None:
        return None
    return data


if __name__ == "__main__":
    with open("test_data/test.jpg", "rb") as f:
        image = f.read()
    print(process_qr_code_image(image))
