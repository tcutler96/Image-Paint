from PIL import Image
import random
import time
import os


# recreates given image in the style of a painting
def paint_image(image_path, quality=5, random_rotate=True, random_order=False, show=True, compare=True, save=False,
                track=True, background_colour=(25, 25, 25), border_size=0., border_colour=(230, 230, 230),
                watermark=False):
    if track:
        t0 = time.time()  # starts timer

    quality = int(quality)  # ensures quality is an integer from 1 to 5
    if quality < 1:
        quality = 1
    elif quality > 5:
        quality = 5
    if border_size < 0:  # ensures border size is not less than 0
        border_size = 0

    if track:
        print('Loading assets...')

    brush_path = 'Images/Main/brush_stroke_pil.png'
    image, pixels, image_width, image_height, image_brush, pixels_brush, brush_pixels, image_brush_width, \
        image_brush_height = load_images(image_path, brush_path)

    if track:
        print('Creating canvas...')

    image_new = create_canvas(image_width, image_height, background_colour, border_size, border_colour)

    if track:
        print('Painting image...')

    image_new = create_image(image_new, pixels, image_width, image_height, image_brush, pixels_brush, brush_pixels,
                             image_brush_height, image_brush_width, quality, random_rotate, random_order,
                             border_size, track, watermark)

    if track:
        t1 = time.time()  # stops timer
        time_taken = str(t1 - t0)
        print('Time taken:', time_taken[:5] + 's')  # time taken

    if show:
        image_new.show()  # displays image

    if save:
        new_path = get_new_path(image_path)
        image_new.save(new_path)  # saves new image

        if track:
            print('Image saved.')

    if compare:
        image_compare = compare_images(image, image_new, border_size, border_colour)  # compares images
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


# determines next available file path name
def get_new_path(image_path):
    file_number = 1
    while os.path.isfile(image_path[:-4] + f'_new_{file_number}' + image_path[-4:]):  # checks file existence
        file_number += 1
    new_path = image_path[:-4] + f'_new_{file_number}' + image_path[-4:]

    return new_path


# loads all required assets
def load_images(image_path, brush_path):
    image = Image.open(image_path)  # opens original image
    image_width, image_height = image.size  # width and height of original image
    pixels = image.load()  # loads image for indexing

    # for brush_path in brush_paths:
    image_brush = Image.open(brush_path)  # opens brush image
    image_brush_width, image_brush_height = image_brush.size  # width and height of brush image
    pixels_brush = image_brush.load()  # loads image for indexing

    brush_pixels = []  # empty list for brush pixels
    for col in range(image_brush_width):  # loops through brush column pixels
        for row in range(image_brush_height):  # loops through brush rows pixels
            brush_colour = pixels_brush[col, row]  # gets colour of current brush pixel
            if brush_colour[3] == 255:  # checks opacity to find non-transparent pixels
                brush_pixels.append((col, row))  # records pixels

    return image, pixels, image_width, image_height, image_brush, pixels_brush, brush_pixels, image_brush_width, \
        image_brush_height


# creates new blank canvas
def create_canvas(image_width, image_height, background_colour, border_size, border_colour):
    if border_size == 0:
        image_new = Image.new('RGB', (image_width, image_height), background_colour)
    else:
        border_width = int(image_width * border_size / 2)
        border_height = int(image_height * border_size / 2)
        inner = Image.new('RGB', (image_width, image_height), background_colour)
        outer = Image.new('RGB', (image_width + 2 * border_width, image_height + 2 * border_height), border_colour)
        outer.paste(inner, (border_width, border_height))
        image_new = outer

    return image_new


# creates new image
def create_image(image_new, pixels, image_width, image_height, image_brush, pixels_brush, brush_pixels,
                 image_brush_height, image_brush_width, quality, random_rotate, random_order, border_size,
                 track, watermark):
    image_brush_width_new = 125 - ((quality - 1) * 25)  # new dimensions for brush image retaining original ratio
    image_brush_height_new = int(image_brush_width_new * (image_brush_height / image_brush_width))
    spacing = (int(image_brush_width_new / 2.5), int(image_brush_height_new / 2.5))

    coords = []  # empty list for coordinates
    for col in range(0, image_width, spacing[0]):  # loops through image column pixels
        for row in range(0, image_height, spacing[1]):  # loops through image rows pixels
            coords.append((col, row))  # records all coordinates
    if random_order:
        coords = random.sample(coords, len(coords))  # randomizes order of coordinates

    percentage = 5  # initial percentage tracker
    for coord in coords:  # loops through list of coordinates
        if track:
            percentage_temp = int(coords.index(coord) / len(coords) * 100)
            if percentage_temp > percentage:  # percentage complete tracker
                print(str(percentage) + '%')
                percentage += 5

        pixel_colour = pixels[coord[0], coord[1]]  # gets colour of current image pixel
        for pix in brush_pixels:
            pixels_brush[pix] = pixel_colour  # colours brush stroke

        # re sizes brush stoke
        image_brush_temp = image_brush.resize((image_brush_width_new, image_brush_height_new), Image.ANTIALIAS)
        if random_rotate:
            image_brush_temp = image_brush_temp.rotate(random.randint(-90, 90))  # randomly rotates brush stroke
        image_new.paste(image_brush_temp, (coord[0] - int(image_brush_width_new / 3) +
                                           int(border_size * image_width * 0.5),
                                           coord[1] - int(image_brush_height_new / 3) +
                                           int(border_size * image_height * 0.5)),
                        image_brush_temp.convert('RGBA'))  # pastes resized coloured brush onto canvas

    if watermark:  # adds watermark to image
        water_image = Image.open('Images/Main/watermark.png')  # loads watermark image
        water_scale = int(image_width * 0.075 / water_image.width)  # scales watermark image
        water_image = water_image.resize((water_scale * water_image.width,
                                          water_scale * water_image.height), Image.ANTIALIAS)
        image_new.paste(water_image, (image_new.width - int(water_image.width * 1.25 +
                                                            border_size * image_width * 0.5),
                                      image_new.height - int(water_image.height * 1.25 +
                                                             border_size * image_height * 0.5)))

    return image_new


# creates collage of original and new image
def compare_images(image, image_new, border_size, border_colour):
    gap = 100  # space between images
    if border_size == 0:
        image_colour = (255, 255, 255)
    else:
        image_colour = border_colour
    image_compare = Image.new('RGB', (image_new.width * 2 + gap, image_new.height), image_colour)  # blank canvas
    # pastes original image
    image_compare.paste(image, (int((image_new.width - image.width) / 2), int((image_new.height - image.height) / 2)))
    image_compare.paste(image_new, (image_new.width + gap, 0))  # pastes new image

    return image_compare


if __name__ == '__main__':
    paint_image(image_path='Images/Image/image_1.jpg', quality=5, random_rotate=True, random_order=False,
                show=True, compare=True, save=False, track=True, background_colour=(25, 25, 25),
                border_size=0.1, border_colour=(230, 230, 230), watermark=False)
