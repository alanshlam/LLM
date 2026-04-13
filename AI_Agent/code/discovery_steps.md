# Steps to identify the video file containing frame_0003.jpg

1. **List directory contents**: Used `ls -F` to identify the video files present in the directory. Found `ch1.mp4` and `ch21.mp4`.
2. **Extract frames**: Used `ffmpeg` to extract the 3rd frame (index 3) from both candidate video files:
   - `ffmpeg -i ch1.mp4 -vf "select=eq(n\,3)" -vframes 1 ch1_frame3.jpg`
   - `ffmpeg -i ch21.mp4 -vf "select=eq(n\,3)" -vframes 1 ch21_frame3.jpg`
3. **Visual Comparison**: Read the extracted images (`ch1_frame3.jpg` and `ch21_frame3.jpg`) and compared them with the target image `frame_0003.jpg`.
4. **Identification**: Determined that the visual content of `ch21_frame3.jpg` matches `frame_0003.jpg`, confirming that the image is from `ch21.mp4`.
