from PIL import Image
import numpy as np
import random
import time
import os


# recreates given image in the style of a painting
def paint_image(image_path, random_rotate=True, random_order=False, show=True, compare=True, save=False,
                track=True, background_colour=(25, 25, 25), border_size=0., border_colour=(230, 230, 230),
                watermark=False):
    if track:
        t0 = time.time()  # starts timer
    if border_size < 0:  # ensures border size is not less than 0
        border_size = 0

    # loads brush strokes and image arrays
    brush_1 = convert_image(Image.open('Images/Main/brush_stroke_numpy_1.png'), True)
    brush_2 = convert_image(Image.open('Images/Main/brush_stroke_numpy_2.png'), True)
    brushes = [brush_1, brush_2]
    brush_width, brush_height, _ = brushes[0].shape
    image = convert_image(Image.open(image_path), True)
    image_width, image_height, _ = image.shape
    # creates canvas array
    canvas = np.full((image_width, image_height, 3), background_colour, dtype=image.dtype)

    if track:
        print('Painting image...')
    # gets list of points to be sampled on image
    sample_points = get_sample_points(image_width, image_height, 10, random_order)
    # create new paint image
    image_new = create_image(image, image_width, image_height, brushes, brush_width, brush_height, canvas,
                             sample_points, random_rotate, track, watermark)
    if border_size > 0:
        image, image_new = add_border(image, image_new, image_width, image_height, border_size, border_colour)

    # converts finished image back to pil format
    image_new = convert_image(image_new, False)

    if track:
        t1 = time.time()  # stops timer
        print('Time taken:', str(np.round(t1 - t0, 2)) + 's')  # time taken
    if show:
        image_new.show()  # displays image
    if save:
        new_path = get_new_path(image_path)
        image_new.save(new_path)  # saves new image
        if track:
            print('Image saved.')

    if compare:
        # combines original and new image for comparison
        image_compare = create_compare(image, image_new, image_width, border_size, border_colour)
        # converts finished image back to pil format
        image_compare = convert_image(image_compare, False)
        if show:
            image_compare.show()  # displays image
        if save:
            new_path = get_new_path(image_path)
            image_compare.save(new_path)  # saves new image
            if track:
                print('Image comparison saved.')

    if compare:
        return image_new, image_compare
    else:
        return image_new


# converts PIL image to numpy array or vice versa
def convert_image(image, to_array=True):
    if to_array:
        return np.array(image)
    else:
        return Image.fromarray(image)


# determines next available file path name
def get_new_path(image_path):
    file_number = 1
    while os.path.isfile(image_path[:-4] + f'_new_{file_number}' + image_path[-4:]):  # checks file existence
        file_number += 1
    new_path = image_path[:-4] + f'_new_{file_number}' + image_path[-4:]
    return new_path


# gets list of points to be sampled on image
def get_sample_points(width, height, step, randomise):
    points = []
    for row in range(2, height, step):
        for col in range(2, width, step):
            points.append((col, row))  # majority of points
        points.append((width - 3, row))  # points along right edge
    for col in range(2, width, step):
        points.append((col, height - 3))  # points along bottom edge
    points.append((width - 3, height - 3))  # point in bottom right corner
    if randomise:  # randomises order of sampled points
        points = random.sample(points, len(points))
    return points


# gets box coordinates of brush and image arrays to be layered
def slice_boxes(coord, b_width, b_height, i_width, i_height):
    b_width, b_height, i_width, i_height = b_width - 1, b_height - 1, i_width - 1, i_height - 1
    # initial box coordinates
    top_left = [coord[0] - b_width // 2 + 4, coord[1] - b_height // 2 + 4]
    bot_right = [coord[0] + b_width // 2 + 4, coord[1] + b_height // 2 + 4]
    canvas_top_left, canvas_bot_right = top_left.copy(), bot_right.copy()
    brush_top_left, brush_bot_right = [[0, 0], [b_width, b_height]]
    # if coordinates are outside of canvas boundaries, trims boxes accordingly
    if top_left[0] < 0:
        canvas_top_left[0] = 0
        brush_top_left[0] = -top_left[0]
    if top_left[1] < 0:
        canvas_top_left[1] = 0
        brush_top_left[1] = -top_left[1]
    if bot_right[0] > i_width:
        canvas_bot_right[0] = i_width
        brush_bot_right[0] = b_width + i_width - bot_right[0]
    if bot_right[1] > i_height:
        canvas_bot_right[1] = i_height
        brush_bot_right[1] = b_height + i_height - bot_right[1]
    return [canvas_top_left, canvas_bot_right], [brush_top_left, brush_bot_right]


# layers brush stroke array onto canvas array by mixing colours
def layer(input):
    return [input[6] * (input[3] - input[0]) + input[0],
            input[6] * (input[4] - input[1]) + input[1],
            input[6] * (input[5] - input[2]) + input[2]]


def create_image(image, image_width, image_height, brushes, brush_width, brush_height, canvas, sample_points,
                 random_rotate, track, watermark):
    percentage = 5  # initial percentage tracker
    for point in sample_points:  # loops through sample points
        if track:
            percentage_temp = int(sample_points.index(point) / len(sample_points) * 100)
            if percentage_temp > percentage:  # percentage complete tracker
                print(str(percentage) + '%')
                percentage += 5
        # gets colour of current point
        colour = image[point]
        # randomly chooses brush stroke
        brush = random.choice(brushes)
        # recolours brush array while retaining alpha channel
        brush[:, :, :-1] = colour
        if random_rotate:
            brush = np.rot90(brush, random.randint(0, 3))
        # gets coordinates of canvas and brush box
        canvas_box, brush_box = slice_boxes(point, brush_width, brush_height, image_width, image_height)
        # gets canvas and brush array slice
        canvas_slice = canvas[canvas_box[0][0]:canvas_box[1][0] + 1, canvas_box[0][1]:canvas_box[1][1] + 1]
        brush_slice = brush[brush_box[0][0]:brush_box[1][0] + 1, brush_box[0][1]:brush_box[1][1] + 1]
        # combines brush and canvas arrays into single array
        combined = np.concatenate((canvas_slice, brush_slice), axis=2).astype('float')
        # preprocesses array to save time
        combined[:, :, 6] = combined[:, :, 6] / 255
        # applies layer function to all elements of array
        layered = np.apply_along_axis(layer, 2, combined).astype('uint8')
        # pastes layered array onto canvas
        canvas[canvas_box[0][0]:canvas_box[1][0] + 1, canvas_box[0][1]:canvas_box[1][1] + 1] = layered
    if watermark:
        water_mark = convert_image(Image.open('Images/Main/watermark.png'), True)  # loads watermark array
        water_width, water_height, _ = water_mark.shape
        scale = int(min(image_width, image_height) * 0.06 / water_width)
        # scales watermark with image size
        if scale > 1:
            water_mark = np.kron(water_mark, np.ones((scale, scale, 1)))
            water_width, water_height, _ = water_mark.shape
        # adds watermark to image
        canvas[image_width - water_width - 25:image_width - 25,
               image_height - water_height - 25:image_height - 25] = water_mark[:, :, 0:3]
    return canvas


# adds border around paint image
def add_border(image, image_new, image_width, image_height, border_size, border_colour):
    border_width, border_height = int(image_width * border_size / 2), int(image_height * border_size / 2)
    image_border = np.full((image_width + border_width * 2, image_height + border_height * 2, 3),
                           border_colour, dtype=image_new.dtype)
    image_new_border = image_border.copy()
    image_border[border_width:-border_width, border_height:-border_height, :] = image
    image_new_border[border_width:-border_width, border_height:-border_height, :] = image_new
    return image_border, image_new_border


def create_compare(image, image_new, image_width, border_size, border_colour):
    if border_size > 0:
        image_compare = np.concatenate((image, image_new), axis=1)
    else:
        border = np.full((image_width, 100, 3), border_colour, dtype=image.dtype)
        image_compare = np.concatenate((image, border, image_new), axis=1)
    return image_compare


if __name__ == '__main__':
    paint_image(image_path='Images/Image/image_1.jpg', random_rotate=True, random_order=False, show=True,
                compare=True, save=False, track=True, background_colour=(25, 25, 25), border_size=0.1,
                border_colour=(230, 230, 230), watermark=False)
