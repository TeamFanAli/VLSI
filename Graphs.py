import numpy as np
import matplotlib.pyplot as plt


def print_hi(name):
    instances = np.array(range(1, 41))
    '''gecode o0 p3 rotation
    times = {
        'vlsi-rot': np.array([.52, .52, .51, .51, .55, .54, .53, .53, .53, .54, 20.45, .54, .53, .71, .69, 240, 1.30,
                              .71, 2.39, 6.83, 2.67, 12.92, 52.36, 7.51, 240.0, 15.06, 9.82, 72.55, 960, 240.0, 240.0,
                              240, 240.0, 240.0, 240.0, 0.60, 12.21, 240, 240.0, 240.0]),
        'x-finder': np.array([.48, .50, .50, .51, .53, .50, .52, .53, .52, .52, 00.54, .52, .51, .70, .66, .70, 0.62,
                              .62, 0.63, 0.65, 0.61, 00.62, 00.59, 0.60, 94.27, 00.59, 0.59, 00.61, 0.5, 0.660, 0.560,
                              0.8, 0.560, 0.560, 0.620, 0.57, 00.61, 0.6, 0.630, 6.250])
    }
    '''

    '''gecode o0 p3
    times = {
        'vlsi':     np.array([.54, .52, .52, .53, .53, .52, .52, .53, .52, .53, 181.65, .53, .56, .57, .54, 240.19,
                              3.32, 1.12, 16.23, 35.62, 9.39, 111.86, 240, 20.91, 240.0, 79.82, 33.56, 225.74, 500, 240, 240,
                              240, 240, 240, 240, .68, 28.1, 240, 500, 500]),
        'x-finder': np.array([.51, .50, .50, .52, .52, .54, .51, .52, .52, .53, 000.58, .55, .56, .55, .55, 000.57,
                              0.54, 0.54, 00.55, 00.58, 0.59, 000.59, .55, 00.57, 16.09, 00.62, 00.60, 000.58, 000, .62, .55,
                              .71, .53, .56, .59, .54, 0.50, .59, 000, 000])
    }
    '''
    width = 1.0
    fig, ax = plt.subplots()

    mask1 = times['vlsi'] < 999
    mask2 = times['vlsi'] >= 999

    ax.bar(instances[mask1], times['vlsi'][mask1], width, label='vlsi', color="C0")
    ax.bar(instances[mask1], times['x-finder'][mask1], width, bottom=times['vlsi'][mask1],
           label='x-finder', color='C1')

    ax.set_ylabel('Average execution times (seconds)')
    ax.plot([240 for _ in range(42)], color="gray", linestyle='--', label="vlsi time limit")
    ax.legend(prop={'size': 20})
    # ax.set_yscale('log')

    plt.xlim(0.5, 40.5)
    plt.ylim(0, 350)
    plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
