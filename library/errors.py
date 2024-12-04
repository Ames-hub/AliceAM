class exited_questioning(Exception):
    def __init__(self):
        self.error_code = 0
    def __str__(self):
        return "The user exited the questioning."

class conflicting_punishments(Exception):
    def __init__(self):
        self.error_code = 1
    def __str__(self):
        return "Two or more punishments are conflicting and cannot be applied at the same time."

class impossible_punishment(Exception):
    def __init__(self, msg):
        self.msg = msg
        self.error_code = 2
    def __str__(self):
        return "The punishment is impossible to apply.\n" + self.msg