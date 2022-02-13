from apnggif import apnggif
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video import fx as vfx
from PIL import Image, ImageSequence


def resizePng(fn):
    im = Image.open(fn)
    (w,h) = im.size
    r=w/h
    if w>h: wh = (512, int(512/r))
    else: wh = (int(512*r), 512)
    if 'duration' in im.info:
        frames = []
        for frame in ImageSequence.Iterator(im):
            frames.append(frame.resize(wh))
        frames[0].save(fn, save_all = True, append_images = frames[1:], duration = im.info['duration'], loop = im.info['loop'], blend = im.info['blend'])
    else:
        im = im.resize(wh)
        im.save(fn)

def gif2webm(fn):
    clip = VideoFileClip(fn, has_mask=True)
    if clip.duration > 3:
        clip = clip.fx(vfx.multiply_speed, final_duration = 3)
    clip.write_videofile(fn.replace(".gif", ".webm"), preset="placebo", with_mask=True, ffmpeg_params=['-auto-alt-ref', '0'])
    clip.close()
    return fn.replace(".gif", ".webm")

def apng2webm(pngfn):
    apnggif(pngfn)
    return gif2webm(pngfn.replace(".png", ".gif"))
