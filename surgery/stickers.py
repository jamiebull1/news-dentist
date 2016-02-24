"""
Create wordclouds (in the shape of stickers).
"""
import os
import random

from wordcloud import WordCloud

import matplotlib.pyplot as plt
from surgery.toothcomb import STOPWORDS


THIS_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(THIS_DIR, "static")


def blues(*args, **kwargs):
    return "hsl(%d, 80%%, 50%%)" % random.randint(175, 250)


def generate(path, img_path):
    img_path = os.path.join(STATIC_DIR, 'img', img_path)
    if os.path.isfile(img_path):
        return
    txt_path = os.path.join(STATIC_DIR, 'teeth', path)
    with open(txt_path, 'r', encoding='utf8') as txt_file:
        text = txt_file.read()
    if not text:
        return
    # take relative word frequencies into account, lower max_font_size
    cloud = WordCloud(
        max_font_size=40,
        stopwords=STOPWORDS,
        relative_scaling=0.5,
        scale=3,
        background_color='white',
        color_func=blues
    ).generate(text)

    plt.figure()
    plt.imshow(cloud)
    plt.axis("off")
    plt.savefig(img_path)
