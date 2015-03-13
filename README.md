# motiontraining
Webcam-based motion tracking for training MRI subjects to lie still in the mock scanner.
- Graphically tracks a colored sticker on subject's nose.  
- Provides subject with quantitative visual feedback on their movements.
- Can pause/play a video playing in VLC media player when the subject moves outside of a configurable range. This may help motivate younger subjects. (Works fine on OSX.  Buggy on Windows for now)

1. Place a small round sticker on the tip of the subject's nose. 1/4-inch fluorescent green dots from <a href="http://www.chromalabel.com/collections/color-coding-dot-stickers-on-rolls/products/1-4-color-code-dots?variant=450574829">chromalabel</a> work perfectly.
2. Place webcam on head coil so that it is pointing at the sticker on their nose.
3. Run <code>python motiontraining.py</code>
4. Once the interface is up, click on the sticker in the image to reset the tracked sticker color.

This package is built on the <a href="http://simplecv.org/">SimpleCV</a> framework.  See INSTALL.txt for instructions on installing SimpleCV and required packages.
