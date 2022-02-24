from apnggif import apnggif
from PIL import Image, ImageSequence
import os


def tryResizePng(fn):
    im = Image.open(fn)
    (w,h) = im.size
    r=w/h
    if w>h: wh = (512, int(512/r))
    else: wh = (int(512*r), 512)
    if 'duration' in im.info:
        framesCnt = 0
        totalDuration = 0
        for frame in ImageSequence.Iterator(im):
            framesCnt += 1
            totalDuration += frame.info['duration']
        return wh, framesCnt / totalDuration * 1000
    else:
        im = im.resize(wh)
        im.save(fn)
    return wh, 1

def gif2webm(fn, wh, fps):
    newfn = fn.replace(".gif", ".webm")
    os.system(f"ffmpeg -hide_banner -loglevel error -y -i {fn} -vf scale={wh[0]}:{wh[1]},fps=fps={fps} -c:v libvpx-vp9 -crf 0 -b:v 500K -t 00:00:03 {newfn}")
    return newfn

def apng2webm(pngfn, wh, fps):
    apnggif(pngfn)
    return gif2webm(pngfn.replace(".png", ".gif"), wh, fps)