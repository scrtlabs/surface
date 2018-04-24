from random import random


class Preprocessor:
    def __init__(self, task, args):
        self.task = task
        self.args = args

    def shuffle(self, inputs):
        """
        Shuffle the values of a list.
        :return:
        """
        return random.shuffle(inputs)
