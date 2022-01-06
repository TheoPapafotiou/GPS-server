# ==================== USING PIL + OPENCV =======================================

# import cv2 
# from PIL import Image
# import numpy as np
# import time

# im2 = Image.open('Server1.jpg')
# im1 = Image.open('Server2.jpg')
# width_init, height_init = im1.size #Initial frame size --> 2304 x 1536

# newsize = (width_init//3, height_init//3)
# im1 = im1.resize(newsize)
# im2 = im2.resize(newsize)

# def get_merged_frame(im1, im2, width, height, color=(0, 0, 0)):
# 	dst = Image.new('RGB', (width_init//2, height_init//2), color)
# 	dst.paste(im1, (0, 0))
# 	dst.paste(im2, (width, height))
# 	return dst

# def nothing(x):
# 	pass

# windowName = "Merge Photos"
# cv2.namedWindow(windowName)

# # If image is resized //2
# cv2.createTrackbar('Width', windowName, 323, 400, nothing)
# cv2.createTrackbar('Height', windowName, 463, 500, nothing)

# # If image is resized //3
# cv2.createTrackbar('Width', windowName, 215, 400, nothing)
# cv2.createTrackbar('Height', windowName, 312, 500, nothing)

# while(1):
# 	time.sleep(0.1)
# 	width = int(cv2.getTrackbarPos('Width', windowName))
# 	height = int(cv2.getTrackbarPos('Height', windowName))

# 	start = time.time()
# 	pil_final = get_merged_frame(im1, im2, width, height)
# 	cv_final = np.array(pil_final) 
	
# 	# Convert RGB to BGR 
# 	cv_final = cv_final[:, :, ::-1].copy()
# 	print("Duration for merging and coverting to cv2 format: ", time.time() - start)

# 	cv2.imshow('Final', cv_final)
# 	k = cv2.waitKey(1) & 0xFF
# 	if k == 27:
# 		break

# cv2.imwrite('Test_merging.jpg', cv_final)
# cv2.destroyAllWindows()


# ==================== USING OPENCV =======================================

import cv2 
import time

im2 = cv2.imread('Server1.jpg')
im1 = cv2.imread('Server2.jpg')
width_init, height_init, _ = im1.shape #Initial frame size --> 2304 x 1536

newsize = (width_init//3, height_init//3)
im1 = cv2.resize(im1, newsize, interpolation = cv2.INTER_AREA)
im2 = cv2.resize(im2, newsize, interpolation = cv2.INTER_AREA)

def get_merged_frame(im1, im2, width, height):
    dst = cv2.imread('1000x800_blank.png')
    x1 = 0
    y1 = 0
    x2 = width
    y2 = height
    
    dst[y1 : y1+newsize(1), x1 : x1+newsize(0)] = im1
    dst[y2 : y2+newsize(1), x2 : x2+newsize(0)] = im2

    return dst

def nothing(x):
	pass

windowName = "Merge Photos"
cv2.namedWindow(windowName)

# If image is resized //2
cv2.createTrackbar('Width', windowName, 323, 400, nothing)
cv2.createTrackbar('Height', windowName, 463, 500, nothing)

# If image is resized //3
cv2.createTrackbar('Width', windowName, 215, 400, nothing)
cv2.createTrackbar('Height', windowName, 312, 500, nothing)

while(1):
	time.sleep(0.1)
	width = int(cv2.getTrackbarPos('Width', windowName))
	height = int(cv2.getTrackbarPos('Height', windowName))

	start = time.time()
	cv_final = get_merged_frame(im1, im2, width, height)
	print("Duration for merging using cv2 format: ", time.time() - start)

	cv2.imshow('Final', cv_final)
	k = cv2.waitKey(1) & 0xFF
	if k == 27:
		break

cv2.imwrite('Test_merging.jpg', cv_final)
cv2.destroyAllWindows()