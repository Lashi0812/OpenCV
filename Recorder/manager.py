import cv2
import numpy as np
from dataclasses import dataclass
from typing import (
    Callable,
    Optional
    )
import time



@dataclass
class WindowManager:
    window_name:str
    keypress_callback:Optional[Callable[[int],None]] = None
    _is_window_created = False
    
    @property
    def is_window_created(self):
        return self._is_window_created
    
    
    def created_window(self):
        cv2.namedWindow(self.window_name)
        self._is_window_created = True
        
    def show(self,frame):
        cv2.imshow(self.window_name,frame)
    
    def destroy_window(self):
        cv2.destroyWindow(self.window_name)
        self._is_window_created = False
        
    def process_event(self):
        keycode = cv2.waitKey(1)
        if self.keypress_callback is not None and keycode != -1:
            self.keypress_callback(keycode)
            

@dataclass
class CaptureManager:
    capture:cv2.VideoCapture
    window_manager:Optional[WindowManager] = None
    show_mirror:bool = True
    
    
    def __post_init__(self):
        self._channel = 0
        self._entered_frame = False
        self._frame = None
        
        self._image_filename:Optional[str] = None
        self._video_filename:Optional[str] = None
        self._video_encoding = None
        self._video_writer:Optional[cv2.VideoWriter] =None
        
        self._start_time:Optional[float] = None
        self._frame_elapsed = 0
        self._fps_estimate = None
        
    @property
    def channel(self):
        return self._channel
    
    @channel.setter
    def channel(self,value):
        if self._channel != value:
            self._channel = 0
            self._frame = None
    
    @property
    def frame(self):
        if self._entered_frame  and self._frame is None:
            _ ,self._frame = self.capture.retrieve(
                self._frame,self.channel
            )
        return self._frame
        
    def enter_frame(self) -> None:
        if self.capture is not None:
            self._entered_frame = self.capture.grab()
            
    def exit_frame(self):
        
        if self._frame is None:
            self._entered_frame = None
            return
        
        if self._frame_elapsed == 0:
            self._start_time = time.perf_counter()
        else:
             time_elapsed = time.perf_counter() - self._start_time
             self._fps_estimate = self._frame_elapsed / time_elapsed
        self._frame_elapsed += 1 
        
        if self.window_manager is not None:
            if self.show_mirror:
                mirror_frame = np.fliplr(self._frame)
                self.window_manager.show(mirror_frame)
            else:
                self.window_manager.show(self._frame)
             
        
        # write the image
        if self._image_filename is not None:
            cv2.imwrite(self._image_filename,self._frame)
            self._image_filename = None
            
        # write the video
        self._write_video()
        
        
        # Release the Frame
        self._frame = None
        self._entered_frame = False
        
    def write_image(self,filename) -> None:
        self._image_filename = filename
        
    def start_rec_video(self,filename:str,
                        encoding = cv2.VideoWriter_fourcc(*"MP4V")):
        self._video_filename = filename
        self._video_encoding = encoding
        
    def stop_rec_video(self):
        self._video_filename  = None
        self._video_encoding  = None
        self._video_writer = None
    
    def _write_video(self):
        
        if self._video_filename is None:
            return
        
        if self._video_writer is None:
            fps = self.capture.get(cv2.CAP_PROP_FPS)
            
            if np.isnan(fps) or fps <= 0.0:
                if self._frame_elapsed < 20:
                    return
                else:
                    fps = self._fps_estimate
            
            size = (int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            
            self._video_writer = cv2.VideoWriter(
                self._video_filename,
                self._video_encoding,
                fps,
                size
            )
            
        self._video_writer.write(self._frame)        