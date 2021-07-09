import cv2 

class Merge_Files:

    def __init__(self):
        self.res_width = self.init_width//3
        self.res_height = self.init_height//3
        
        self.coor_width = 215
        self.coor_height = 312
        
        self.init_width = 2304
        self.init_height = 1536

        self.x1 = 0
        self.y1 = 0
        self.x2 = self.coor_width
        self.y2 = self.coor_height

    def get_merged_frame(self, im1, im2):
        dst = cv2.imread('1000x800_blank.png')
        
        dst[self.y1 : self.y1+self.res_height, self.x1 : self.x1+self.res_width] = im1
        dst[self.y2 : self.y2+self.res_height, self.x2 : self.x2+self.res_width] = im2

        return dst