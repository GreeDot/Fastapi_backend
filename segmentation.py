import cv2
import numpy as np
import os

#이미지랑 경로 넣으면 해당 경로에 마스크랑 리사이즈된 이미지 저장된 return값은 무시해도됨 디버그용
def segmentImage(image, output_path = "./"):
    image = cv2.imread(image)
    imageList = []
    saved_paths = []
    # 새로운 너비 설정 (400픽셀)
    new_width = 400
    # 종횡비를 유지하기 위한 새로운 높이 계산
    original_height, original_width = image.shape[:2]
    new_height = int((new_width / original_width) * original_height)

    # 이미지 리사이즈
    resized_image = cv2.resize(image, (new_width, new_height))
    imageList.append(('Resized Image', resized_image))

    # Assuming you have the bounding box coordinates (x, y, width, height)
    height, width = resized_image.shape[:2]
    x, y, w, h = 0, 0, width, height  # Replace with your bounding box coordinates
    roi = resized_image[y:y+h, x:x+w]

    # Convert to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    imageList.append(('Grayscale Image', gray))

    # Apply adaptive thresholding
    # 논문값
    C = 0
    filterW = 7
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, filterW, C
    )
    imageList.append(('Thresholded Image', thresh))

    # Perform morphological closing
    kernel = np.ones((3, 3), np.uint8)
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    imageList.append(('Morphological Closing', closing))

    # Dilate the image
    dilated = cv2.dilate(closing, kernel, iterations=1)
    imageList.append(('Dilated Image', dilated))

    # Add 10 pixels of padding around the image
    dilated_padded = cv2.copyMakeBorder(dilated, 100, 100, 100, 100, cv2.BORDER_CONSTANT, value=0)
    imageList.append(('Dilated Image with Padding', dilated_padded))

    # Flood filling
    flood_fill = dilated_padded.copy()
    h, w = flood_fill.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(flood_fill, mask, (0, 0), 255)
    imageList.append(('Flood Fill Image', flood_fill))

    # Remove the 10-pixel padding
    flood_fill = flood_fill[100:-100, 100:-100]
    imageList.append(('Flood Fill Image without Padding', flood_fill))

    # Invert flood filled image
    flood_fill_inv = cv2.bitwise_not(flood_fill)
    imageList.append(('Inverted Flood Fill Image', flood_fill_inv))

    # Combine the two images to get the foreground
    out = dilated | flood_fill_inv
    imageList.append(('Combined Image', out))

    # Find and retain only the largest polygon
    contours, _ = cv2.findContours(out, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    mask = np.zeros_like(out)
    cv2.drawContours(mask, [largest_contour], -1, 255, thickness=cv2.FILLED)
    imageList.append(('Largest Contour Mask', mask))

    # Apply the mask to the original ROI
    result = cv2.bitwise_and(roi, roi, mask=mask)
    imageList.append(('Result', result))

    # Save the 'Largest Contour Mask' and 'Resized Image' to the specified output path
    for name, img in imageList:
        if name in ('Largest Contour Mask', 'Resized Image'):
            file_path = os.path.join(output_path, f"{name.replace(' ', '_')}.png")
            cv2.imwrite(file_path, img)
            saved_paths.append(file_path)  # 저장된 각 파일의 경로를 리스트에 추가

    return saved_paths

