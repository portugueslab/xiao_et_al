import numpy as np
from matplotlib import collections
from matplotlib import pyplot as plt
from svgpath2mpl import parse_path

from xiao_et_al_utils.defaults import FIGURES_PATH

"""
# Configure matplotlib for the figures:
plt.rcParams["axes.linewidth"] = 0.5
plt.rcParams["axes.labelsize"] = 8
plt.rcParams["legend.fontsize"] = 8
plt.rcParams["axes.titlesize"] = 8
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["pdf.use14corefonts"] = True

for t in ["x", "y"]:
    plt.rcParams[t + "tick.major.size"] = 3
    plt.rcParams[t + "tick.labelsize"] = 8
    plt.rcParams[t + "tick.major.width"] = 0.5
"""


def save_figure(name, fig=None, subfolder="imaging", dpi=600, **kwargs):
    if fig is None:
        fig = plt.gcf()
    fig.patch.set_alpha(0.0)
    dest_dir = FIGURES_PATH / subfolder
    dest_dir.mkdir(exist_ok=True, parents=True)
    fig.savefig(str(dest_dir / f"{name}.svg"), transparent=True, dpi=dpi, **kwargs)


def despine(ax, sides=["right", "top"], rmticks=True):
    """Fine-tuned despine function not to depend on less controllable seaborn one."""
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
    """Plot the siluhette of a fish."""
    path_fish = "m0 0c-13.119 71.131-12.078 130.72-12.078 138.78-5.372 8.506-3.932 18.626-3.264 23.963-6.671 1.112-2.891 4.002-2.891 5.114s-2.224 8.005.445 9.116c-.223 3.113.222 0 0 1.557-.223 1.556-3.558 3.558-2.891 8.227.667 4.67 3.558 10.228 6.226 9.784 2.224 4.892 5.559 4.669 7.56 4.447 2.001-.223 8.672-.445 10.228-6.004 5.115-1.556 5.562-4.002 5.559-6.67-.003-3.341.223-8.45-3.113-12.008 3.336-4.224.667-13.786-3.335-13.786 1.59-8.161-2.446-13.786-3.558-20.679-2.223-34.909-.298-102.74 1.112-141.84"
    path = parse_path(path_fish)
    min_p = np.min(path.vertices, 0)
    path.vertices -= min_p
    f = np.abs(path.vertices[:, 1]).max() * scale
    path.vertices[:, 0] = path.vertices[:, 0] / f
    path.vertices[:, 1] = path.vertices[:, 1] / f

    path.vertices += np.array(offset)

    collection = collections.PathCollection(
        [path], linewidths=0, facecolors=["#909090"]
    )
    ax.add_artist(collection)
