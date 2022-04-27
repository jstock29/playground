import random

import generativepy.color
from generativepy.bitmap import Scaler
from generativepy.nparray import make_nparray_data, save_nparray, load_nparray, make_npcolormap, apply_npcolormap, \
    save_nparray_image
from generativepy.color import Color
import math
import numpy as np
import streamlit as st
from numba import jit
from alive_progress import alive_bar

N_COMBOS = 99 * 3
MAX_COUNT = 1_000_000
# A = round(random.uniform(-3, 3),3)
# B = round(random.uniform(-3, 3),3)
# C = round(random.uniform(-1.5, 1.5),3)
# D = round(random.uniform(-1.5, 1.5),3)

A = 2.879879
B = -0.765145
C = -0.966918
D = 0.744728
COLORS = list(generativepy.color.cssColors.keys())


def paint_tinkerbell(image, pixel_width, pixel_height, frame_no, frame_count):
    scaler = Scaler(pixel_width, pixel_height, width=3, startx=-2, starty=-2)

    x = 0.01
    y = 0.01
    for i in range(MAX_COUNT):
        x, y = x * x - y * y + A * x + B * y, 2 * x * y + C * x + D * y
        if x > pixel_width:
            x = pixel_width
        if y > pixel_height:
            y = pixel_height

        px, py = scaler.user_to_device(x, y)
        if px > pixel_width:
            px = pixel_width - 2
        if py > pixel_height:
            py = pixel_height - 2
        image[py, px] += 1


@jit(nopython=True)
def next_xy(x, y, choice, a, b, c, d):
    if choice == 1:
        x, y = math.sin(a * x) + b * math.sin(a * y), math.sin(c * x) + d * math.sin(c * y)
    elif choice == 2:
        x, y = math.cos(a * x) + b * math.sin(a * y), math.cos(c * x) + d * math.sin(c * y)
    elif choice == 3:
        x, y = math.sin(a * x) + b * math.cos(a * y), math.sin(c * x) + d * math.cos(c * y)
    elif choice == 4:
        x, y = math.cos(a * x) + b * math.cos(a * y), math.cos(c * x) + d * math.cos(c * y)
    return x, y


def paint_kings_fractal(image, pixel_width, pixel_height, frame_no, frame_count):
    scaler = Scaler(pixel_width, pixel_height, width=4, startx=-2, starty=-2)

    x = 2
    y = 2
    misses = 0
    choice = random.choice([1, 2, 3, 4])
    with alive_bar(int(MAX_COUNT)) as bar:
        for i in range(MAX_COUNT):
            x, y = next_xy(x, y, choice, A, B, C, D)

            try:
                px, py = scaler.user_to_device(x, y)
                image[py, px] += 1
            except IndexError:
                misses += 1
            bar()
    print(misses)


def colorise(counts, colors: list, background: str, normalization: float = 0.25):
    color_list = [Color(background)] + [Color(color) for color in colors]
    counts = np.reshape(counts, (counts.shape[0], counts.shape[1]))
    power_counts = np.power(counts, normalization)
    maxcount = np.max(power_counts)
    normalised_counts = (power_counts * 1023 / max(maxcount, 1)).astype(np.uint32)

    colormap = make_npcolormap(1024, color_list)

    outarray = np.zeros((counts.shape[0], counts.shape[1], 3), dtype=np.uint8)
    apply_npcolormap(outarray, normalised_counts, colormap)
    return outarray


def main():
    st.title('Generative art env')

    global A
    global B
    global C
    global D
    global MAX_COUNT

    if st.checkbox('Manual'):
        in1, in2, in3 = st.columns(3)
        col0, col1, col2 = st.columns(3)
        with in1:
            dimension = int(st.number_input('Size', 500, 10000, 1000))
            background = st.selectbox('Background', ['black', 'white'])
        with in2:
            combos = int(st.number_input('Combos', 0, 10000, 0))
            colors = st.multiselect('Colors', COLORS)
        with in3:
            MAX_COUNT = int(st.number_input('N Points', 10000, 1_000_000_000, 1_000_000))
            normalization = st.number_input('Normalization', 0., 1., 0.25)
        if len(colors) >= 3:
            for combo in range(combos):
                id = random.getrandbits(32)

                A = round(random.uniform(-3, 3), 4)
                B = round(random.uniform(-3, 4), 4)
                C = round(random.uniform(-1.5, 1.5), 4)
                D = round(random.uniform(-1.5, 1.5), 4)
                data = make_nparray_data(paint_kings_fractal, dimension, dimension, channels=1)
                save_nparray("/tmp/temp.dat", data)
                data = load_nparray("/tmp/temp.dat")
                frame = colorise(data, colors, background, normalization=normalization)
                col = combo % 3
                save_nparray_image(f'outputs/fractal-dream-{id}.png', frame)

                if col == 0:
                    with col0:
                        st.write(A, B, C, D)
                        st.write(f'outputs/fractal-dream-{id}.png')
                        st.image(frame)
                if col == 1:
                    with col1:
                        st.write(A, B, C, D)
                        st.write(f'outputs/fractal-dream-{id}.png')
                        st.image(frame)
                if col == 2:
                    with col2:
                        st.write(A, B, C, D)
                        st.write(f'outputs/fractal-dream-{id}.png')
                        st.image(frame)

    else:
        in1, in2, in3 = st.columns(3)
        with in1:
            dimension = int(st.number_input('Size', 500, 10000, 1000))
            normalization = st.number_input('Normalization', 0., 1., 0.25)

        with in2:
            combos = st.number_input('Combos', 0, 10000, 0)
        with in3:
            MAX_COUNT = int(st.number_input('N Points', 10000, 1_000_000_000, 1_000_000))

        if combos > 0:
            col0, col1, col2 = st.columns(3)

            for combo in range(combos):
                id = random.getrandbits(32)

                background = random.choice(['black', 'white'])
                n_colors = random.choice([2, 3, 4, 5])
                colors = []
                for c in range(n_colors):
                    colors.append(random.choice(COLORS))
                A = round(random.uniform(-3, 3), 4)
                B = round(random.uniform(-3, 4), 4)
                C = round(random.uniform(-1.5, 1.5), 4)
                D = round(random.uniform(-1.5, 1.5), 4)
                data = make_nparray_data(paint_kings_fractal, dimension, dimension, channels=1)

                save_nparray("/tmp/temp.dat", data)
                data = load_nparray("/tmp/temp.dat")
                frame = colorise(data, colors, background, normalization=normalization)
                save_nparray_image(f'outputs/fractal-dream-{id}.png', frame)

                col = combo % 3
                if col == 0:
                    with col0:
                        st.write(A, B, C, D)
                        st.write(f'outputs/fractal-dream-{id}.png')
                        st.image(frame)
                if col == 1:
                    with col1:
                        st.write(A, B, C, D)
                        st.write(f'outputs/fractal-dream-{id}.png')
                        st.image(frame)
                if col == 2:
                    with col2:
                        st.write(A, B, C, D)
                        st.write(f'outputs/fractal-dream-{id}.png')
                        st.image(frame)


def combos():
    pass


if __name__ == '__main__':
    main()
