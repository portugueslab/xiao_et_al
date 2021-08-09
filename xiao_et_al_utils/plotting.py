from svgpath2mpl import parse_path
from matplotlib import collections
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.pyplot import Figure
from pathlib import Path


def _add_lettering(f, letter, s=0.05, **kwargs):
    letter_ax = f.add_axes((0, 1 - s, s, s))
    letter_ax.text(0, 0, letter, ha="left", va="top", fontsize=14, **kwargs)
    letter_ax.set(xlim=(0, 1), ylim=(-1, 0))

    letter_ax.axis("off")

    return letter_ax


class LetteredFigure(Figure):
    def __init__(self, letter, *args, **kwargs):
        self.letter = letter

        super().__init__(*args, **kwargs)
        self.patch.set_alpha(0.)
        _add_lettering(self, letter.upper())

    def savefig(self, folder, **kwargs):
        super().savefig(str(folder / f"fig_{self.letter}.pdf"), transparent=True,
                        **kwargs)


def plot_config():
    # plt.rcParams['figure.constrained_layout.use'] = True
    plt.rcParams['axes.linewidth'] = 0.5
    plt.rcParams['axes.labelsize'] = 8
    plt.rcParams["legend.fontsize"] = 8
    plt.rcParams["axes.titlesize"] = 8
    for t in ["x", "y"]:
        plt.rcParams[t + 'tick.major.size'] = 3
        plt.rcParams[t + 'tick.labelsize'] = 8
        plt.rcParams[t + 'tick.major.width'] = 0.5


def despine(ax, sides=["right", "top"], rmticks=True):
    if sides == "all":
        sides = ["right", "top", "left", "bottom"]
    if rmticks:
        if sides == "all":
            ax.set(xticks=[], yticks=[])
        if "left" in sides:
            ax.set(yticks=[])
        if "bottom" in sides:
            ax.set(xticks=[])
    [ax.axes.spines[s].set_visible(False) for s in sides]


def add_fish(ax, offset=(0, 0), scale=1):
    path_fish = 'm0 0c-13.119 71.131-12.078 130.72-12.078 138.78-5.372 8.506-3.932 18.626-3.264 23.963-6.671 1.112-2.891 4.002-2.891 5.114s-2.224 8.005.445 9.116c-.223 3.113.222 0 0 1.557-.223 1.556-3.558 3.558-2.891 8.227.667 4.67 3.558 10.228 6.226 9.784 2.224 4.892 5.559 4.669 7.56 4.447 2.001-.223 8.672-.445 10.228-6.004 5.115-1.556 5.562-4.002 5.559-6.67-.003-3.341.223-8.45-3.113-12.008 3.336-4.224.667-13.786-3.335-13.786 1.59-8.161-2.446-13.786-3.558-20.679-2.223-34.909-.298-102.74 1.112-141.84'
    path = parse_path(path_fish)
    min_p = np.min(path.vertices, 0)
    path.vertices -= min_p
    f = np.abs(path.vertices[:, 1]).max() * scale
    path.vertices[:, 0] = path.vertices[:, 0] / f
    path.vertices[:, 1] = path.vertices[:, 1] / f

    path.vertices += np.array(offset)

    collection = collections.PathCollection([path],
                                            linewidths=0,
                                            facecolors=["#909090"])
    ax.add_artist(collection)