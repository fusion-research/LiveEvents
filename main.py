import sys
import time

import matplotlib.pyplot as plt
import click
import numpy as np

from PyProbEC.cep import get_evaluation
from eventGeneration.eventGeneration import get_events
from videoFeed.videoFeed import VideoFeed


def update_evaluation(evaluation, new_evaluation):
    for event, event_val in new_evaluation.items():
        if event in evaluation:
            for ids, ids_val in event_val.items():
                if ids in evaluation[event]:
                    for timestamp, prob in ids_val.items():
                        evaluation[event][ids][timestamp] = prob
                else:
                    evaluation[event][ids] = ids_val
        else:
            evaluation[event] = event_val

    return evaluation


def update_graph(fig, ax, line1, evaluation, graph_x_size):
    x_data = sorted(evaluation['interesting']['()'].keys())
    y_data = [evaluation['interesting']['()'][k] for k in x_data]

    # print('x_data', x_data)
    # print('y_data', y_data)

    # Find which range we want to show based on the data we have
    max_data = x_data[-1]
    right = max(max_data, graph_x_size)
    left = right - graph_x_size

    # Increase the range by 10% on each side to make it less cramped
    left -= graph_x_size / 10
    right += graph_x_size / 10

    ax.set_xlim(left, right)

    line1.set_xdata(x_data)
    line1.set_ydata(y_data)
    fig.canvas.draw()
    fig.canvas.flush_events()


@click.command()
@click.option('-w', '--max_window', default=10)
@click.option('--cep_frequency', default=8)
@click.option('-g', '--group_size', default=16)
@click.option('-f', '--group_frequency', default=8)
@click.option('--graph_x_size', default=100)
def start_detecting(max_window, cep_frequency, group_size, group_frequency, graph_x_size):
    if max_window < cep_frequency:
        print('The window of events can not be smaller than the frequency of checking', file=sys.stderr)
        sys.exit(-1)

    x = np.linspace(0, graph_x_size, graph_x_size)
    y = np.linspace(0, 1, graph_x_size)

    # You probably won't need this if you're embedding things in a tkinter plot...
    plt.ion()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    line1, = ax.plot(x, y, 'r-')  # Returns a tuple of line objects, thus the comma

    # for phase in np.linspace(0, 10*np.pi, 500):
    #     line1.set_ydata(np.sin(x + phase))
    #     fig.canvas.draw()
    #     fig.canvas.flush_events()

    video_input = VideoFeed()

    window = []
    events = []

    evaluation = {}

    for i, frame in enumerate(video_input):
        if i > 500:
            break

        # Keep only the number of frames we need
        window.append((i, frame))
        window = window[-group_size:]

        # Every group_frequency, get the relevant events
        if not (i + 1) % group_frequency:
            # Check that we have enough frames for the group (preventing errors on first iterations)
            if len(window) >= group_size:
                relevant_frames = window[-group_size:]

                events += get_events(relevant_frames)

        # Every cep_frequency frames, run the CEP part with the relevant events
        if not (i + 1) % cep_frequency and events:
            # Remove the events that happened before the current window
            while events and events[0].timestamp < i - max_window:
                # While we have events and the first event is before the current window, remove the first event
                events = events[1:]

            new_evaluation = get_evaluation(
                timestamps=np.arange(i - cep_frequency + 1, i + 1),
                input_events=events
            )

            evaluation = update_evaluation(evaluation, new_evaluation)

            update_graph(fig, ax, line1, evaluation, graph_x_size)

            # time.sleep(1)

    print(evaluation)


if __name__ == '__main__':
    start_detecting()

# import matplotlib.pyplot as plt
# import numpy as np
#
# x = np.linspace(0, 6*np.pi, 100)
# y = np.sin(x)
#
# # You probably won't need this if you're embedding things in a tkinter plot...
# plt.ion()
#
# fig = plt.figure()
# ax = fig.add_subplot(111)
# line1, = ax.plot(x, y, 'r-')  # Returns a tuple of line objects, thus the comma
#
# for phase in np.linspace(0, 10*np.pi, 500):
#     line1.set_ydata(np.sin(x + phase))
#     fig.canvas.draw()
#     fig.canvas.flush_events()