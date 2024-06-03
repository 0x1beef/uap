import os

class FrameSequence:
    def __init__(self, frames_dir, fps):
        self.frames_dir = frames_dir
        self.fps = fps
        import glob
        self.num_frames = len(glob.glob(f'{self.frames_dir}/frame_*.png'))
    def get_frame(self, frame):
        import cv2
        return cv2.imread(f'{self.frames_dir}/frame_{frame:04d}.png', cv2.IMREAD_GRAYSCALE)
    def get_frame_count(self):
        return self.num_frames
    def get_frame_time(self, frame):
        return frame / self.fps
    def get_fps(self):
        return self.fps
    
def get_fps(video):
    command = f'ffprobe -v 0 -of csv=p=0 -select_streams v:0 -show_entries stream=r_frame_rate "{video}"'
    import subprocess, shlex, fractions
    fps_str = subprocess.check_output(shlex.split(command)).decode("utf-8").strip()
    return float(fractions.Fraction(fps_str))
    
def extract_frames(video, frames_dir, filters):
    if not os.path.exists(f'{frames_dir}/frame_0000.png'):
        # note: without the variable frame rate option this would produce some duplicate frames
        output_frames = f'-vsync vfr -start_number 0 {frames_dir}/frame_%04d.png'
        os.system(f'ffmpeg -i "{video}" -vf "{filters}" {output_frames}')

def gimbal_extract_frames(video, frames_dir):
    # note: crop can sometimes be off by a pixel, so make sure it's exact
    extract_frames(video, frames_dir, filters='format=gray, crop=428:428:104:27:exact=1')

def gimbal_from_huggingface():
    video = 'gimbal/2 - GIMBAL.wmv'
    if not os.path.exists(video):
        import utils
        utils.download_from_huggingface(f'logicbear/uap/{video}')
    frames_dir = 'gimbal'
    gimbal_extract_frames(video, frames_dir)
    return FrameSequence(frames_dir, get_fps(video))

# interpolate values in a dataframe's fields around the switch from WH to BH
def gimbal_fix_wh_to_bh(df, fields, minus = 10, plus = 0):
    first_black_hot = 372
    interp_range = range(first_black_hot - minus, first_black_hot + plus)
    import utils
    return utils.interpolate_rows(df, interp_range, fields)