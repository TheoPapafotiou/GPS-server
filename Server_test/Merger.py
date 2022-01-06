import cv2 

class Merge_Files:

    def __init__(self):
        self.coor_width = 215+50+10
        self.coor_height = 360+20+20
        
        self.init_width = 2304
        self.init_height = 1536
        
        self.res_width = self.init_width//3
        self.res_height = self.init_height//3
        self.res_size = (self.res_width, self.res_height)
        self.res_width = 960
        self.res_height = 540

        self.x1 = 0
        self.y1 = 0
        self.x2 = self.coor_width
        self.y2 = self.coor_height

    def get_merged_frame(self, im1, im2):
        dst = cv2.imread('1500x1000_blank.png')
        
#         im1 = cv2.resize(im1, self.res_size, interpolation = cv2.INTER_AREA)
#         im2 = cv2.resize(im2, self.res_size, interpolation = cv2.INTER_AREA)
        
        dst[self.y1 : self.y1+self.res_height, self.x1 : self.x1+self.res_width] = im1
        dst[self.y2 : self.y2+self.res_height, self.x2 : self.x2+self.res_width] = im2

        return dst