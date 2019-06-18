import time
from matplotlib import pyplot as plt
from matplotlib import patches

from PyProbEC.model import Model

NUMBER_EXECUTIONS = 5

test_file = 'example/test.pl'

EVENT_NAMES = {
    'interesting': 'Video Only',
    'abuse': 'Video + Object Detection',
    'run_over': 'Run Over',
}


def get_evaluation(timestamps, input_events=()):
    event_definition_files = [
        'anomalyDetection/event_defs.pl',
    ]

    model = Model(event_definition_files)

    return model.get_probabilities(timestamps, input_events=input_events)


# def create_graph(evaluation, filename):
#     fig, ax = plt.subplots(1)
#
#     for event in evaluation:
#         already_plotted = []
#
#         for ids in evaluation[event]:
#             if set(ids) not in already_plotted:
#                 to_plot = False
#
#                 values_x = []
#                 values_y = []
#
#                 for timepoint, prob in sorted(evaluation[event][ids].items(), key=lambda x: x[0]):
#                     values_x.append(timepoint)
#                     values_y.append(prob)
#
#                     # if prob > 0:
#                     #     print('{0} -> {1} -> {2} -> {3}'.format(event, str(ids), timepoint, prob))
#                     #     to_plot = True
#                     print('{0},{1},{2}'.format(timepoint, prob, event))
#                     to_plot = True
#
#                 if to_plot:
#                     ax.plot(values_x, values_y, label=EVENT_NAMES.get(event, event))
#
#                     already_plotted.append(set(ids))
#
#         # if already_plotted:
#     # If we have plotted something
#     # ax.title('Probability of an anomaly happening across the frames')
#
#     plt.xlabel('Frame')
#     plt.ylabel('Probability')
#
#     plt.legend()
#
#     # plt.show()
#     plt.savefig('OutputGraphs/' + filename + '_85_aux.png', bbox_inches='tight')