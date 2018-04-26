from random import randint


class Preprocessor:
    def __init__(self, task, args):
        self.task = task
        self.args = args

    def rand(self):
        """
        Return a random integer.
        :return:
        """
        return randint(0, 127)
