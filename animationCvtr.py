

from apnggif import apnggif
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video import fx as vfx
from PIL import Image, ImageSequence

def resizeAnimatedPng(fn):
    im = Image.open(fn)
    (w,h) = im.size
    r=w/h
    if w>h:
        newW = 512
        newH =int(512/r)
    else:
        newW = int(512*r)
        newH = 512
    frames = []
    for frame in ImageSequence.Iterator(im):
        frames.append(frame.resize((newW, newH)))
    frames[0].save(fn, save_all = True, append_images = frames[1:], duration = im.info['duration'], loop = im.info['loop'], blend = im.info['blend'])

def apng2gif(fn):
    apnggif(fn)

def gif2webm(fn, w=None, h=None, r=None):
    clip = VideoFileClip(fn, has_mask=True)
    if clip.duration>3:
        clip = clip.fx(vfx.multiply_speed, final_duration=3)
    clip.write_videofile(fn.replace(".gif", ".webm"), preset="placebo", with_mask=True, ffmpeg_params=['-auto-alt-ref', '0'])
    clip.close()

def apng2webm(pngfn):
    resizeAnimatedPng(pngfn)
    apng2gif(pngfn)
    gif2webm(pngfn.replace(".png", ".gif"))