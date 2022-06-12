import numpy

from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d


from optimizer import PervaporationFunction


def plot_diffusion_curve(
    function: PervaporationFunction,
    t: float,
) -> None:
    x = numpy.arange(0, 1, 0.01)
    y = numpy.array([
        function(_x, t) for _x in x
    ])

    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    ax.plot(x, y)
    ax.set_xlabel('Feed')
    ax.set_ylabel('Penetration')
    ax.set_title('Experiment bla bla')
    plt.savefig('anywhere.jpg')  # TODO: add configs


def plot_diffusion_surface(
    function: PervaporationFunction,
    t_min: float,
    t_max: float,
    # TODO: optional scatter experiment data
) -> None:
    x = numpy.linspace(0, 1, 100)
    t = numpy.linspace(t_min, t_max, 100)

    v_function = numpy.vectorize(function)
    x_grid, t_grid = numpy.meshgrid(x, t)
    p = v_function(x_grid, t_grid)

    fig = plt.figure(figsize=(16, 9))
    ax = plt.axes(projection='3d')
    ax.plot_surface(
        x_grid, t_grid, p,
        rstride=1, cstride=1,
        cmap='viridis', edgecolor='none'
    )
    ax.set_xlabel('Feed')
    ax.set_ylabel('Temperature')
    ax.set_zlabel('Penetration')
    ax.set_title('Experiment bla bla')
    plt.savefig('anywhere_3d.jpg')  # TODO: add configs
