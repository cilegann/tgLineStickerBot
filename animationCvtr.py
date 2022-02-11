

from apnggif import apnggif
from moviepy.video.io.VideoFileClip import VideoFileClip

from moviepy.video.io.ffmpeg_writer import ffmpeg_write_video

def apng2gif(fn):
    apnggif(fn)

def gif2webm(fn):
    clip = VideoFileClip(fn, has_mask=True)
    clip.write_videofile(fn.replace(".gif", ".webm"), preset="placebo", with_mask=True, ffmpeg_params=['-auto-alt-ref', '0'])

def apng2webm(fn):
    apng2gif(fn)
    gif2webm(fn.replace(".png", ".webm"))
    apnggif(fn)
