from __future__ import print_function
import time

from problog.program import PrologString
from problog import get_evaluatable

from itertools import groupby

from os import path
import sys


# Files that define how EC works
PROBLOG_FILES = [
    'PyProbEC/ProbLogFiles/prob_ec_cached.pl',
    'PyProbEC/ProbLogFiles/prob_utils_cached.pl',
]


def unsorted_groupby(iterable, key=None):
    return groupby(sorted(iterable, key=key), key=key)


def term_to_list(term):
    if term.args:
        return [term.args[0].value] + term_to_list(term.args[1])
    else:
        return []


class Model(object):
    def __init__(self, event_definition_files=()):
        # The base model will be formed from the base ProbLog files that define EC
        # and the files given by the user that should define the rules for the
        # complex event they are trying to detect
        models = [
            self.read_model(m)
            for m in PROBLOG_FILES + event_definition_files
        ]

        self.model = '\n\n'.join(models)

    @staticmethod
    def _get_values(aux):
        term = aux[0]
        prob = aux[1]

        gen_event = term.args[0].args[0]

        event = gen_event.functor
        ids = gen_event.args
        timepoint = term.args[1].value

        return event, ids, timepoint, prob

    @staticmethod
    def _evaluation_to_prob(evaluation):
        # event -> ids -> timepoint -> prob
        return {
            event: {
                ids: {
                    timepoint: list(v3)[0][3]
                    for timepoint, v3 in unsorted_groupby(list(v2), key=lambda x: x[2])
                }
                for ids, v2 in unsorted_groupby(list(v1), key=lambda x: str(x[1]))
            }
            for event, v1 in unsorted_groupby(map(Model._get_values, evaluation.items()), lambda x: x[0])
        }

    def get_timepoints(self):
        model = PrologString(self.model + '\n\nquery(allTimePoints(TPs)).')

        knowledge = get_evaluatable().create_from(model)

        timepoints = [
            term_to_list(term.args[0])
            for term in knowledge.evaluate().keys()
            if term.functor == 'allTimePoints'
        ]

        return sorted([item for sublist in timepoints for item in sublist])

    def get_values_for(self, timepoints, input_events=()):
        # As the model we use self.model (basic EC definition + definition of rules by the user) and we add the list
        # of the input events
        string_model = self.model + '\n' + '\n'.join(map(lambda x: x.to_problog(), input_events))

        updated_knowledge = ''

        res = {}

        for timepoint in timepoints:
            for event in ['interesting', 'abuse']:
                # query = 'query(holdsAt({event}(ID1, ID2) = true, {timepoint})) :- allIDs(IDs), ' \
                #         'cartesianUnique(IDs, IDs, Tuples), member(Tuple, Tuples), ' \
                #         'Tuple = [ ID1, ID2 ].\n'.format(event='following', timepoint=timepoint)
                query = 'query(holdsAt({event} = true, {timepoint})).\n'.format(event=event, timepoint=timepoint)

                model = PrologString(string_model + '\n' + updated_knowledge + '\n' + query)

                knowledge = get_evaluatable().create_from(model)

                evaluation = knowledge.evaluate()

                res.update(evaluation)

                for k, v in evaluation.items():
                    if v > 0.0:
                        updated_knowledge += '{0}::{1}.\n'.format(v, k).replace('holdsAt', 'holdsAt_')

        return res

    def get_probabilities(self, timepoints, input_events=()):
        evaluation = self.get_values_for(timepoints, input_events=input_events)

        return self._evaluation_to_prob(evaluation)

    @staticmethod
    def read_model(m):
        if path.exists(m):
            with open(m) as f:
                return f.read()
        else:
            print('{} not found'.format(m), file=sys.stderr)
            return '\n'