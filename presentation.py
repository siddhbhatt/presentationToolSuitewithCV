import numpy as np
import cv2
import math
import pyautogui 
import pygetwindow as gw
import threading
import speech_recognition as sr
import wx
app = wx.App(False)
widthScr, heightScr = wx.GetDisplaySize()
def mouse():
    cap=cv2.VideoCapture(0)
    bg=cv2.flip(cap.read()[1],1)
    roi_bg = bg[10:450, 350:630].copy()
    kernel = np.ones((5,5), np.uint8)
    x1,y1 = 50,50
    for c in gw.getAllTitles():
        if 'PowerPoint' in c:
            win = gw.getWindowsWithTitle(c)[0]
    win.minimize()
    win.restore()
    pyautogui.press(['shift', 'f5'])
    while True:
        fg=cv2.flip(cap.read()[1],1)
        #print(fg.shape)
        cv2.rectangle(fg, (350,10), (630,450), (0,255,0),0)
        roi_fg = fg[10:450, 350:630].copy()
        diff = cv2.absdiff(roi_bg,roi_fg)
        diff=cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
        #threshhold
        diff=cv2.threshold(diff,10,255,0)[1]
        #morph operations
        diff=cv2.erode(diff,cv2.getStructuringElement(cv2.MORPH_ERODE,(2,2)),iterations=2)
        diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)
        diff = cv2.dilate(diff, kernel, iterations=3)
        #contours
        contours, hierarchy = cv2.findContours(diff,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        try:
            c=max(contours, key = cv2.contourArea)
            ctr = cv2.drawContours(roi_fg, c, -1, (0,255,0), 10)
            extTop = tuple(c[c[:, :, 1].argmin()][0])
            #draw circle
            cv2.circle(img=roi_fg, center=extTop, radius=20, color=(255,0,0),thickness =-1)
            x1 = math.ceil(extTop[0]/roi_fg.shape[1]*widthScr)
            y1 = math.ceil(extTop[1]/roi_fg.shape[0]*heightScr)
            pyautogui.moveTo(x1, y1, duration = 0.5)        #added duration delay of 0.5s
        except:
            pass
        #merge to orginal frame
        x_offset=350
        y_offset=10
        fg[y_offset:y_offset+roi_fg.shape[0], x_offset:x_offset+roi_fg.shape[1]] = roi_fg
        #cv2.imshow('frame', fg)  
        keypress = cv2.waitKey(1) & 0xFF
        if keypress == ord("q"):
            pyautogui.press('esc')
            break
    cap.release()
    cv2.destroyAllWindows()
def readVoice(r):
    with sr.Microphone() as source:                # use the default microphone as the audio source
        audio = r.listen(source)                   # listen for the first phrase and extract it into audio data  
    try:
        print("You said " + r.recognize_google(audio))    # recognize speech using Google Speech Recognition
        return r.recognize_google(audio)
    except LookupError:                            # speech is unintelligible
        print("Could not understand audio")
        return "error"
    
def voice(r, rules):
    while True:
        try:
            str = readVoice(r)
            for key,vals in rules.items():
                if str in vals:
                    print(key)
                    pyautogui.press(key)
        except Exception as e:
            print (e)
            pass
    
if __name__ == "__main__":
    try:
        t1 = threading.Thread(target=mouse, name='t1')
        t1.start()
        r = sr.Recognizer()
        rules={
            "down":["down slide","down slide please","next slide please","next slide","go next slide", "next page"],
            "up":["up slide","up slide please","previous slide please","previous slide","go previous slide", "previous page"],
            "exit":["escape","exit","esc"]
                
        }
        t2 = threading.Thread(target=voice(r,rules), name='t2')
        t2.start()
        t2.join()
        #break
    except KeyboardInterrupt:
        sys.exit(0)
