# Documentation reference: 
# How to access metadata using this node: https://docs.lumeo.com/docs/custom-function-node#accessing-metadata 
# Examples, e.g. how to send webhooks: https://docs.lumeo.com/docs/custom-function-node#examples

from lumeopipeline import VideoFrame  # Lumeo lib to access frame and metadata, only available in the Lumeo containers
import cv2

# Global variables that persist across frames go here.
# Onetime initialization code can also live here.
frame_count = 0

# This function is an example of a custom function that prints the frame count and sets a frame level metadata field
# It follows the same signature as the "process_frame" function required in a custom function.
# The idea is to call this function from the "process_frame" function, and return the result.
def process_frame(frame: VideoFrame, **kwargs) -> bool:

    # Insert your code here.
    global frame_count
    frame_count = frame_count + 1

    with frame.data() as mat:

        # Here's an example that uses OpenCV to put arbitrary text on the frame
        cv2.putText(mat, "Frame " + str(frame_count), (50,50), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 255), 1)

        # Here's an example of how to access the frame level metadata an print on the frame
        meta = frame.meta()
        yidx = 100
        for (key, value) in meta.get_all().items(): 
            cv2.putText(mat, key + " : " + str(value), (50,yidx), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
            yidx = yidx + 50

        # Add your own metadata to the frame
        meta.set_field("frame_count", frame_count)
        meta.save()


    # Return False to drop this frame, True to continue processing.
    return True