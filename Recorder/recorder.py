import cv2
from manager import CaptureManager,WindowManager



class Recorder:
    def __init__(self) -> None:
        self._window_manager = WindowManager("Recorder",
                                             self.on_key_press)
        self._capture_manager = CaptureManager(
            cv2.VideoCapture(0),self._window_manager,show_mirror=True           
        )
        
    def run(self):
        self._window_manager.created_window()
        while self._window_manager.is_window_created:
            self._capture_manager.enter_frame()
            frame = self._capture_manager.frame
            
            if frame is not None:
                pass
            
            self._capture_manager.exit_frame()
            self._window_manager.process_event()
            
            
    def on_key_press(self,keycode:int):
        if keycode == 32:
            self._capture_manager.write_image("../images/screenshot.png")
        elif keycode == 9:
            if not self._capture_manager._video_filename:
                self._capture_manager.start_rec_video("../videos/screen.mp4")
            else:
                self._capture_manager.stop_rec_video()
            
        elif keycode == 27:
            self._window_manager.destroy_window()
            

if __name__ == "__main__":
    Recorder().run()