import re
import os

from chrome_store import chrome_store


class Functions:
    @staticmethod
    def chrome_init(parser, client_id, client_secret, refresh_token):
        parser.variables['client_id'] = client_id
        parser.variables['client_secret'] = client_secret
        parser.variables['refresh_token'] = refresh_token
        parser.variables['chrome_store'] = chrome_store.ChromeStore(client_id,
                                                                    client_secret,
                                                                    refresh_token)

    @staticmethod
    def chrome_new(parser, filename):
        try:
            store = parser.variables['chrome_store']
        except KeyError:
            raise InvalidStateException('You must run chrome.new function before uploading an extension.')

        store.upload(filename, True)


class Parser:
    functions = {
        'chrome.init': Functions.chrome_init,
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
        func(self, *tokens[1:])

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


class InvalidStateException(Exception):
    pass
