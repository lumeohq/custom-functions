from lumeopipeline import VideoFrame  # Auto added by Lumeo
import cv2                    # Auto added by Lumeo
import numpy                  # Auto added by Lumeo
from urllib.request import urlopen

first_run = True
watermark_overlay = None
LUMEO_LOGO_URL = "https://assets.lumeo.com/media/logo/lumeo-blackbg-vertical-80.png"


def process_frame(frame: VideoFrame, image_url = LUMEO_LOGO_URL, **kwargs) -> bool:

    global watermark_overlay
    global first_run

    with frame.data() as mat:
        try:
            if first_run == True:
                # Get pipeline resolution
                width = frame.video_info().width
                height = frame.video_info().height            
                
                # Get watermark image from URL
                (wH, wW, watermark) = download_watermark_from_url(image_url, height, width)
                # print("watermark: {} {} image: {} {}".format(wH,wW,height, width))
                
                # If we have one, set the watermark overlay. 
                if watermark is not None:
                    watermark_overlay = numpy.zeros((height,width,4), dtype="uint8")
                    watermark_overlay[height-wH:height, width-wW:width] = watermark
                
                first_run = False

            if watermark_overlay is not None:
                cv2.addWeighted(watermark_overlay, 1.0, mat, 1.0, 0, mat)

        except Exception as error:
            print(error)
            pass

    return True

def download_watermark_from_url(image_url, max_height, max_width):
    global LUMEO_LOGO_URL
    if not image_url or len(image_url) == 0:
        image_url = LUMEO_LOGO_URL
    
    wH = None
    wW = None
    watermark = None

    try:
        print("Downloading watermark from url: {}".format(image_url))
        watermarkimage = numpy.asarray(bytearray(urlopen(image_url).read()), dtype="uint8")
        watermark = cv2.imdecode(watermarkimage, cv2.IMREAD_UNCHANGED)
        if watermark.shape[2] != 4:
            watermark = cv2.cvtColor(watermark,cv2.COLOR_BGR2BGRA)
        (wH, wW) = watermark.shape[:2]
        
        height = wH
        width = wW
        if width > max_width:
            scale = max_width / width
            wW = width = int(scale * width)
            wH = height = int(scale * height)
            
        if height > max_height:
            scale = max_height / height
            wH = height = int(scale * height)
            wW = width = int(scale * width)
            
        watermark = cv2.resize(watermark, (width, height), interpolation = cv2.INTER_AREA)
        
    except Exception as e:
        print("Error extracting watermark from url ({}) : {}".format(image_url,str(e)))
        wH = None
        wW = None
        watermark = None
        
    return (wH, wW, watermark)
  