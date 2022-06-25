import matplotlib.pyplot as plt


def plot(line, **kwargs):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(line, **kwargs)
    return fig
