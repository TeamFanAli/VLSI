import numpy as np
import matplotlib.pyplot as plt


def main():
    instances = np.array(range(1, 41))
    '''SAT
    times = {
        'vlsi': np.array([.79, .61, 1.15, 1.56, 3.87, 6.16, 8.95, 21.34, 21.82, 52.51]),
    }
    
    SAT rotations
    {8.6418, 4.9872, 13.1758, 33.0891,
        89.0046, 206.007, 257.0805}
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
    '''
    standard smt
    {0.04, 0.06, 0.08, 0.10, 0.17, 0.23, 0.21, 0.20, 0.21, 0.67, 12.36, 1.73, 1.13, 0.66, 1.70, 18.76, 1.58 3.66, 68.48, 47.48, 56.83, 300, 32.86, 8.16, 300, 300, 24.59, 64.50, 64.32, 300, 7.88, 300, 3.16, 300, 300, 300, 300, 300, 300, 300}}
    '''
    """
    SMT with rotations
{0.06, 0.09, 0.14, 0.18, 0.71, 0.85, 5.17, 5.72, 3.39, 28.56, 300, 113.03, 115.83, 300, 38.69, 300, 300, 300, 300, 300, 300, 300, 300, 209.596, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300}    """

    standard = [.79, .61, 1.15, 1.56, 3.87, 6.16, 8.95, 21.34, 21.82, 52.51, 300, 300, 300, 300, 300, 300, 300, 300,
                300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300]
    rotation = [8.64, 4.98, 13.17, 33.08,
                89.00, 206.00, 257.08, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300,
                300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300]
    '''
    standard = [0.04, 0.06, 0.08, 0.10, 0.17, 0.23, 0.21, 0.20, 0.21, 0.67, 12.36, 1.73, 1.13, 0.66, 1.70, 18.76, 1.58, 3.66,
                68.48, 47.48, 56.83, 300, 32.86, 8.16, 300, 300, 24.59, 64.50, 64.32, 300, 7.88, 300, 3.16, 300, 300, 300, 300, 300, 300, 300]
    rotation = [0.06, 0.09, 0.14, 0.18, 0.71, 0.85, 5.17, 5.72, 3.39, 28.56, 300, 113.03, 115.83, 300, 38.69, 300, 300, 300,
                300, 300, 300, 300, 300, 209.59, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300]
                '''
    width = 0.8
    fig, ax = plt.subplots()

    standard_mask1 = np.array(standard) >= 300
    standard_mask2 = np.array(standard) < 300
    rotation_mask1 = np.array(rotation) >= 300
    rotation_mask2 = np.array(rotation) < 300

    rects1_hatch = ax.barh(instances[rotation_mask1], np.array(rotation)[rotation_mask1] * -1, width,
                           color='white', hatch='/////', edgecolor='C0', linewidth=0)
    rects1 = ax.barh(instances[rotation_mask2], np.array(rotation)[rotation_mask2] * -1, width,
                     label="SAT-rotations", color='C0')
    rects2_hatch = ax.barh(instances[standard_mask1], np.array(standard)[standard_mask1], width,
                           color='white', hatch='/////', edgecolor='C1', linewidth=0)
    rects2 = ax.barh(instances[standard_mask2], np.array(standard)[
                     standard_mask2], width, label="SAT", color='C1')

    ax.set_xlabel('Average execution times (seconds)')
    ax.set_ylabel('Instances')
    ax.set_yticks(range(1, 41))
    ax.set_xticks(range(-300, 301, 50))
    ax.set_xticklabels([300, 250, 200, 150, 100, 50,
                        0, 50, 100, 150, 200, 250, 300])
    ax.legend(prop={'size': 15})

    ax.bar_label(rects1, padding=3, labels=np.array(rotation)[rotation_mask2])
    print(rotation_mask1)
    ax.bar_label(rects1_hatch, padding=3, labels=[
                 300 for _ in np.array(rotation)[rotation_mask1]])
    ax.bar_label(rects2, padding=3)
    ax.bar_label(rects2_hatch, padding=3)

    fig.tight_layout()

    plt.xscale('symlog')
    ax.set_xticks([-100, -10, -1, 0, 1, 10, 100])
    ax.set_xticklabels([100, 10, 1, 0, 1, 10, 100])
    plt.ylim(0.5, 40.5)
    plt.xlim(-900, 900)
    plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
