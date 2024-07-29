import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

#allow us to perform various operating system-related tasks
import os

#variables
#height and width of slide
width, height = 1280,720

#folder where the slides are present
folderPath = "slides"

#setting up the camera
cap = cv2.VideoCapture(0)
cap.set(3,width)
cap.set(4,height)

#get the presentation images in list
pathimages = sorted(os.listdir(folderPath),key=len)
print(pathimages)

#variables
imgnumber = 0

#height and width of the cam in slide
hs ,ws = int(15*15), int(30*15)

#if the value is below thershold i.e., above the line, then detect the gesture
gestureThreshold = 300

#whwnever it presses the button, we wait till it presses the other one
buttonPressed = False
butttonCounter = 0

#it is a value i.e., no of frames (ex 30 frames = 1 sec) (it should not accept another buttonpress)
buttonDelay = 30

#annotation list for drawing (whenever the index finger is rised)
#also we fill it with different gesture signs to differentiate it between one annotation to another
annotations = [[]]
annotationumber = 0

#it becomes true whenever one finger is put on the screen(i.e., draw pointer)
annotationstart = False

#handdectector, detector confidence in '.',maximum number of hands
detector = HandDetector(detectionCon=0.8,maxHands=1)

while True:
    #importing images
    success,img = cap.read() 
    img = cv2.flip(img, 1)    
    pathfullimage = os.path.join(folderPath, pathimages[imgnumber])
    imgcurrent = cv2.imread(pathfullimage)

    #putting the hands on the screen
    hands, img = detector.findHands(img)

    #put up a line on the screen,(255, 255, 0) is line colour, 6 is the thickness of the line
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (255, 255, 0) ,6)

    #we get the landmark of this hand also no of fingers up
    if hands and buttonPressed is False:
        #it is a list having multiple hands
        #we put 0 because we only need the first one
        hand = hands[0]

        #this checks how many fingers are up and gives us a list
        fingers = detector.fingersUp(hand)
        cx,cy = hand['center']
        #print(fingers)

        #landmark list where no '8' is the index finger
        #constrain values for easier drawing  i.e., we dont have to move hands all around the screen instead to a limited area
        lmList = hand['lmList']  
       
        #Setting up the range, changing this value from 0 to total width
        xval = int(np.interp(lmList[8][0],[width//2,w],[0,width]))

        #cutting pixels from top and bottom
        yval = int(np.interp(lmList[8][1],[150,height-150],[0,height]))

        indexFinger = xval,yval


        #if hand is at the height of the face
        if cy <= gestureThreshold:
            annotationstart = False

            #gesture 1 - left
            if fingers == [1,0,0,0,0]:
                annotationstart = False
                print("left")
                
                #we do this condition so that it does not go out of bound
                if imgnumber > 0:
                    buttonPressed = True
                    annotations = [[]]
                    annotationumber = 0
                    imgnumber-=1
          
            #gesture 2 - right
            if fingers == [0,0,0,0,1]:
                annotationstart = False
                print("right")

                #we do this condition so that it does not go out of bound
                if imgnumber < len(pathimages)-1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationumber = 0
                    imgnumber+=1
          

            if fingers == [1,1,1,1,1]:
                print("No Action")

            if fingers == [0,0,0,0,0]:
                print("No Action")

        
        #gesture 3 - show pointer
        if fingers == [0,1,1,0,0]:
            #we darw the pointer on the slide (imgcurrent) and not on the images, give color and we want it filled
            cv2.circle( imgcurrent, indexFinger, 12, (0,225,0), cv2.FILLED)
            annotationstart = False

        #gesture 4 - draw
        if fingers == [0,1,0,0,0]: 

            if annotationstart is False:
                annotationstart = True
                annotationumber +=1

                #we keep adding the points i.e., append index finger to the annotations list
                annotations.append([])

            #we darw the pointer on the slide (imgcurrent) and not on the images, give color and we want it filled
            cv2.circle(imgcurrent, indexFinger, 12, (0,225,0), cv2.FILLED)
            annotations[annotationumber].append(indexFinger)

        else:
            #becase when the reading gesture is not index finger then we have to stop appending it to the list
            annotationstart = False

        #gesture 5 - erase
        if fingers == [0,1,1,1,0]:
            #checking if there are any annotations present before removing them
            if annotations:
                if annotationumber >= 0:
                    annotations.pop(-1)
                    annotationumber -= 1
                    buttonPressed = True

    else:
        annotationstart = False


    #button pressed iteratios
    if buttonPressed:
        butttonCounter+=1
        if butttonCounter > buttonDelay:
            butttonCounter = 0
            buttonPressed = False

    for i in range (len(annotations)):
        #iterating through every points
        for j in range(len(annotations[i])):
            if j!=0:
                #draw the line in a certain color and line's width
                cv2.line(imgcurrent, annotations[i][j - 1], annotations[i][j], (0,0,200),13)

    #adding the webcam on slide
    imgsmall = cv2.resize(img,(ws,hs))

    #height, width, the channel 
    h,w,_ = imgcurrent.shape
    imgcurrent[0:hs, w-ws:w] = imgsmall

     # Resizing the slide image for better visibility
    imgcurrent = cv2.resize(imgcurrent, (width, height))

    cv2.imshow("image", img)
    cv2.imshow("slides", imgcurrent)

    cv2.imshow("image",img)
    key = cv2.waitKey(1)
    #exit the setup when a key is pressed(i.e., inside the "ord()")
    if key == ord('q') :
        break
