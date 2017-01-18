import re
import os


class Functions:
    def chrome_new(*args):
        print("chrome_new, args: {}".format(args))


class Parser:
    functions = {
        'chrome.new': Functions.chrome_new
    }

    def __init__(self, script=None, script_fn=None):
        super().__init__()
        if (not script and not script_fn) or (script and script_fn):
            raise ValueError("One of script or script_fn must be set!")

        if script_fn:
            self.script = open(script_fn).readlines()
        else:
            self.script = script

        self.variables = {}

    def execute(self):
        for line in self.script:
            self.execute_line(line)

    def execute_line(self, line: str):
        tokens = line.strip().split(" ")
        tokens = self.resolve_variables(tokens)

        # actually execute
        func = self.functions[tokens[0]]
        func(*tokens[1:])

    def token_to_func(self, token):
        try:
            return self.functions[token]
        except KeyError:
            raise FunctionNotDefinedException(token)

    def resolve_variables(self, tokens):
        res = []
        for token in tokens:
            res.append(self.resolve_variable(token))

        return res

    def resolve_variable(self, token: str):
        match = re.match(r'\s*\$\{([^}]+)\}\s*', token)
        if match:
            var = match.group(1)
            if var.startswith('env.'):
                # environment variable
                var = var.split('.', maxsplit=1)[1]
                value = os.getenv(var)
            else:
                # normal variable - read from self
                try:
                    value = self.variables[var]
                except KeyError:
                    raise VariableNotDefinedException(var)

            print("{} -> {}".format(var, value))
            return value
        else:  # token is not a variable, just return it
            print("{} is not a variable token".format(token))
            return token


class VariableNotDefinedException(Exception):
    pass


class FunctionNotDefinedException(Exception):
    pass
