from paint_image_pil import paint_image as paint_pil
from paint_image_np import paint_image as paint_np
import os
import numpy as np
import time


# recreates given images in the style of a painting
def paint_multiple(image_name, method, quality, random_rotate, random_order, show, compare, save, track,
                   background_colour, border_size, border_colour, watermark):
    t0 = time.time()  # starts timer
    image_formats = ['.jpg', '.png', '.gif', '.bmp', '.eps']  # compatible image formats
    file_number = 0
    while True:
        file_number += 1  # increments file number
        file_found = False
        for image_format in image_formats:  # loops through formats
            path = f'Images/{image_name}/{image_name.lower()}_{file_number}'  # current image path
            if os.path.isfile(f'{path}{image_format}'):  # checks if current image + format exists
                path = f'{path}{image_format}'  # adds format to image path
                print(f'Processing {path}...')
                if method == 'pil':
                    paint_pil(path, quality, random_rotate, random_order, show, compare, save, track,
                              background_colour, border_size, border_colour, watermark)  # calls function
                elif method == 'numpy':
                    paint_np(path, random_rotate, random_order, show, compare, save, track,
                             background_colour, border_size, border_colour, watermark)  # calls function

                file_found = True
                break
        if not file_found:  # if no file found
            break  # break while loop
    t1 = time.time()  # stops timer
    print('Time taken:', str(np.round(t1 - t0, 2)) + 's')  # time taken


if __name__ == '__main__':
    paint_multiple(image_name='Image', method='pil', quality=5, random_rotate=True, random_order=False,
                   show=False, compare=True, save=True, track=False, background_colour=(25, 25, 25),
                   border_size=0.1, border_colour=(230, 230, 230), watermark=False)
