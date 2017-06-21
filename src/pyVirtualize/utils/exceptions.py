__author__ = 'rramchandani'


class TimeOutException(Exception):
    message = "There was a system timeout before operation could be able to complete."


class BuildError(Exception):
    message = "Invalid Build ID"

class LoginError(Exception):
    message = "It's mandatory be logged in; to execute this operation."

class RacetrackError(Exception):
    pass

class ProgramNotExecuted(Exception):
    message = "Program couldn't be executed within the Guest."

class TaskExecutionFailed(Exception):
    message = "Task couldn't get executed."