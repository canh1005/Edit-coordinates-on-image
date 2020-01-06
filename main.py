import numpy as np
import cv2
import os
import json
import keyboard
import ctypes

btn_down = False
idx = -1
curidx = -1
FINAL_LINE_COLOR = (0, 0, 0)

def get_points(im):
    ## Set up data to send to mouse handler
    data = {}
    data['im'] = im.copy()
    data['lines'] = []
    #print(data['lines'])
    ## Set the callback function for any mouse event
    #while True:
    cv2.imshow("Image", im)
    cv2.setMouseCallback("Image", mouse_handler, data)
    
    cv2.waitKey(0)
    
    ## Convert array to np.array in shape n,2,2
    #points = np.uint16(data['lines'])
    points = np.float32(data['lines'])
    return points, data['im']

def mouse_handler(event, x, y, flags, data):
    global btn_down
    global lst_polys
    global img_t
    global idx
    global curidx
    global list_poly

    #print(len(data['lines']))
    #print(btn_down)
    if event == cv2.EVENT_LBUTTONUP and btn_down:
        #if you release the button, finish the line
        btn_down = False
        curidx
        idx
        print("curidx",curidx)
        print("idx",idx)
        #lst_pts.append((x, y))
        data['lines'][0].append((x, y)) #append the seconf point
        #print(data['lines'])
        ##Get the index of coordinates in the list
        for sub_point in list_poly:
            cv2.circle(data['im'], sub_point, 2, (255, 0, 255), 5, 16)
            if((x,y) == sub_point):
                idx = list_poly.index((x,y))
                #print(idx)
            #else:
                #print(idx)
        ##Edit the coordinates in the selected position with another position if index has been change
        if(curidx != idx):
            list_poly[idx] = (x,y)
            print("List of points after being edited: ",list_poly)
            idx = -1    
        cv2.circle(data['im'], (x, y), 2, (0, 0, 255),5)
        cv2.imshow("Image", data['im'])

    ##If the mouse is at the coordinates available in the coordinates list, draw a circle with a different color
    elif event == cv2.EVENT_MOUSEMOVE:
        if btn_down == False:
            for sub_point in list_poly:
                if(sub_point == (x,y)):
                    cv2.circle(data['im'],(x,y),1,(0, 255, 255),5)
            cv2.imshow("Image", data['im'])
                        
        

    elif event == cv2.EVENT_LBUTTONDOWN and len(data['lines']) < 2:
        btn_down = True
        curidx = -1
        arr_lst = list_poly
        print(arr_lst)
        #print('one point')
        data['im'] = img_t.copy()
        data['lines'].insert(0,[(x, y)]) #prepend the point
        cv2.circle(data['im'], (x, y), 1, (0, 0, 255), 5)
        ##Get the index of coordinates in the list
        for sub_point in list_poly:
            cv2.circle(data['im'], tuple(sub_point), 2, (255, 0, 255), 5, 16)
            if((x,y) == sub_point):
                curidx = list_poly.index((x,y))
                #print(curidx)
            #else:
                ##print(curidx)
                #print(x,y)
        #print(lst_pts) 
        cv2.polylines(data['im'],np.int32([arr_lst]),1,(255,0,0),thickness=2)
        
        cv2.imshow("Image", data['im'])
        
        #print(data['lines'])
        if len(data["lines"])==2:
            del data['lines'][-1]

def on_key_press():
    global list_poly
    global pre_path
    c = [float(x[0])  for x in list_poly]
    d = [float(x[1])  for x in list_poly]
    final_lst = list(zip(c,d))
    #print("final_lst: \n",final_lst[1][0])
    #print("dtype of 1 element in final_lst: ",type(final_lst[1][0]))
    #data = {'polys':final_lst}
    with open(pre_path,'r') as f:
        json_f = json.load(f)
        json_f['polys'] = final_lst        
    while True:  # making a loop
               
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('s'):  # if key 's' is pressed
                messageBox = ctypes.windll.user32.MessageBoxW
                returnValue = messageBox(None,"Do you want to save?","Question?",32 | 0x1) 
                if returnValue == 1:
                    with open(pre_path, 'w') as f:
                        json.dump(json_f, f, indent=4)
                    #print('File is save!')
                    ctypes.windll.user32.MessageBoxW(0, "File is save!", "Done!", 0x40)
                    break  # finishing the loop
                elif returnValue == 2:
                    ctypes.windll.user32.MessageBoxW(0, "Cancel!", "Done!", 0)
        except:
            break
            
        
# Running the code
## Open Image
if not os.path.exists('Imgs'):
    os.makedirs('Imgs')
img_path = "./Imgs"
imgname = input("enter image file name: ")
filename = os.path.splitext(imgname)[0]
image = os.path.join(img_path,imgname)
#print(image)
if os.path.isfile(image):
    img = cv2.imread(image, 1)
else:
    ctypes.windll.user32.MessageBoxW(0, "Image not exist", "Warning!",0x30)
    exit()
img_t = img
w,h = img.shape[:2]
ext = '.json' 
## read json from the obtained results
if not os.path.exists('Output'):
    os.makedirs('Output')
path = "./Output"
pre_path = os.path.join(path,filename + ext)
if os.path.isfile(pre_path):
    with open(pre_path,'r') as file:
        pred = json.load(file)
else:
    ctypes.windll.user32.MessageBoxW(0, "File json not exist", "Warning!",0x30)
    exit()
##Get list of coordinates in json file
lst_polys = pred['polys']
print("List of points in json file: \n",lst_polys)
print(type(lst_polys))
##If the coordinates in the list are less than 1 then multiply by the height and width of the image
fst_x = np.float32(lst_polys[0][0])
fst_y = np.float32(lst_polys[0][1])
if fst_x<1 or fst_x<1:
    a = [np.float32(x[0]* w)  for x in lst_polys]
    b = [np.float32(x[1]* h)  for x in lst_polys]
            
else:
    a = [np.float32(x[0])  for x in lst_polys]
    b = [np.float32(x[1])  for x in lst_polys]                

#print(a)
#print("dtype of a: ",type(a[0]))
##The list of coordinates has a float32 data type
list_poly = list(zip(a, b))
print("The list of points has a float32 data type:\n ",list_poly) 
print("",type(list_poly))
pts, final_image = get_points(img)
cv2.imshow('Image', final_image)
#print("points: ",pts)
on_key_press()
cv2.waitKey(0)



