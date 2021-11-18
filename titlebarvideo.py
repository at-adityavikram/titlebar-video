from ctypes import *
import os
from subprocess import Popen, CREATE_NEW_CONSOLE 
import win32gui
import win32process
from time import sleep
from pytube import *
from PIL import Image
import numpy as np
import cv2
from pytube import YouTube

user32=windll.user32
kernel32=windll.kernel32
FPS=10

def get_hwnds_for_pid(pid):
	def callback(hwnd, hwnds):
		if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
			_, found_pid = win32process.GetWindowThreadProcessId(hwnd)
			if found_pid == pid:
				hwnds.append(hwnd)
		return True
	hwnds = []
	win32gui.EnumWindows(callback,hwnds)
	return hwnds

def setWindowText(hwnd, text):
    user32.SetWindowTextW(hwnd,text)

def create_window(title,width,height,x,y):
    p = Popen(["cmd.exe"],creationflags=CREATE_NEW_CONSOLE)
    hwnd=None
    while not hwnd:
        hwnd=get_hwnds_for_pid(p.pid)
    hwnd=hwnd[0]
    user32.SetWindowPos(hwnd,0,x,y,width,height,0)
    setWindowText(hwnd,title)
    return hwnd

def close_window(hwnd):
    user32.PostMessageW(hwnd,0x0010,0,0)

def download_video(url):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    stream.download(filename = 'video.mp4')
    print('video downloaded')

def to_gray(r, g, b):
    gs = r*0.2989 + g*0.5870 + b*0.1140
    if gs <=20:
        return "  "
    elif gs >20 and gs <= 50:
        return ".."
    elif gs >50 and gs <= 100:
        return "::"
    elif gs > 100 and gs <=140:
        return "--"
    elif gs > 140 and gs <= 160:
        return "=="
    elif gs > 160 and gs <= 180:
        return "**"
    elif gs > 180 and gs <= 210:
        return "##"
    elif gs > 210 and gs <= 240:
        return "%%"
    elif gs > 240 and gs <= 255:
        return "@@"

def extract_frames(pathIn, pathOut,skip):
    numframes=0
    try:
        os.mkdir(pathOut)
    except:
        pass
    cap = cv2.VideoCapture(pathIn)
    count = 0
    i=0
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            if i > skip - 1:
                print('Read %d frame: ' % count, ret,end='\r')
                cv2.imwrite(os.path.join(pathOut, "frame{:d}.jpg".format(count)), frame)
                i=0
                numframes+=1
            count += 1
            i+=1
        else:
            break
    cap.release()
    cv2.destroyAllWindows()
    return numframes

def add_frame(scn):
    mscn=[]
    try:
        img = Image.open(scn)
    except FileNotFoundError:
        print('!!! not found !!!',scn)
    h = 40
    w = int((img.width / img.height) * h)
    h= h//2
    img = img.resize((w,h), Image.ANTIALIAS)
    img_arr = np.asarray(img)
    h,w,c = img_arr.shape
    for x in range(h):
        tim=""
        for y in range(w):
            pix = img_arr[x][y]
            tim += str(to_gray(pix[0], pix[1], pix[2]))
        mscn.append(tim)
    return '\n'.join(mscn)

def vid2ascii(skip=6):
    nframes = extract_frames('./video.mp4','./frames',skip)
    cur=''
    for i in range(nframes):
        cur += add_frame(f'frames\\frame{(i+1)*skip}.jpg') + 'V'
        print(f'added frame {(i+1)*skip}',end='\r')   
        os.remove(f'frames\\frame{(i+1)*skip}.jpg')
    with open('video.txt','w', encoding='utf-8') as foo:
        foo.write(cur)
    os.remove('./video.mp4')

def main():
    frames=[]
    if os.path.exists('video.txt'):
        with open('video.txt') as f:
            frames=f.read().split('V')
    else:
        if not os.path.exists('video.mp4'):
            download_video(str(input('enter youtube url: ')))
        vid2ascii()
        with open('video.txt') as f:
            frames=f.read().split('V')
    height=len(frames[0].split('\n'))
    width=len(frames[0].split('\n')[0])
    hwnds=[create_window(" ",1200,30,10,10+i*30) for i in range(height)]
    for i in frames:
        for j in range(len(i.split('\n'))):
            setWindowText(hwnds[j],i.split('\n')[j])
        sleep(1/FPS)
    for i in hwnds: close_window(i)

if __name__=="__main__":
    main()