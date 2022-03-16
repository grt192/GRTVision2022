import cv2

'''
Frame is the image.
Text is a tuple representing the text you want on the frame, from top to bottom.
Text will be put on the bottom left corner of the frame.
'''
def put_text_group(frame, text):
    h, w, _ = frame.shape
    offset = 5

    font = cv2.FONT_HERSHEY_PLAIN
    font_scale = 0.7
    font_color = (255, 255, 255)
    font_thickness = 2
    text_x = offset
    text_delta_y = 16
    text_y = h - offset - (text_delta_y * (len(text) - 1))

    for t in text:
        cv2.putText(frame, t, (text_x, text_y), font, font_scale, font_color, font_thickness)
        text_y += text_delta_y

