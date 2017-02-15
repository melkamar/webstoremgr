import re
import os
import time

from webstore_manager.chrome_store import chrome_store
from webstore_manager import logging_helper, util

logger = logging_helper.get_logger(__file__)


class ChromeFunctions:
    @staticmethod
    def read_store(parser):
        try:
            return parser.variables['chrome_store']
        except KeyError:
            raise InvalidStateException('You must run chrome.new function before uploading an extension.')

    @staticmethod
    def init(parser, client_id, client_secret, refresh_token):
        parser.variables['client_id'] = client_id
        parser.variables['client_secret'] = client_secret
        parser.variables['refresh_token'] = refresh_token
        parser.variables['chrome_store'] = chrome_store.ChromeStore(client_id,
                                                                    client_secret,
                                                                    refresh_token)

    @staticmethod
    def set_app(parser, app_id):
        store = ChromeFunctions.read_store(parser)
        parser.variables['app_id'] = app_id
        store.app_id = app_id
        store.update_item_url = "https://www.googleapis.com/upload/chromewebstore/v1.1/items/{}".format(app_id)

    @staticmethod
    def new(parser, filename):
        store = ChromeFunctions.read_store(parser)
        store.upload(filename, True)

    @staticmethod
    def update(parser, filename):
        store = ChromeFunctions.read_store(parser)
        store.upload(filename, False)

    @staticmethod
    def publish(parser, target):
        store = ChromeFunctions.read_store(parser)
        if target == 'public':
            store.publish(chrome_store.ChromeStore.TARGET_PUBLIC)
        elif target == 'trusted':
            store.publish(chrome_store.ChromeStore.TARGET_TRUSTED)
        else:
            raise ValueError('Unknown value {}. Expected one of public, trusted.'.format(target))

    @staticmethod
    def check_version(parser, expected_version, timeout=30):
        store = ChromeFunctions.read_store(parser)
        version = ''
        timeout = int(timeout)  # if it was passed from the user, it will be a str

        correct = False
        start = time.time()
        while time.time() - start < timeout:
            version = store.get_uploaded_version()
            if version == expected_version:
                correct = True
                break

            logger.warn(
                "Expecting version {}, but obtained {}. Will keep retrying for {} seconds.".format(expected_version,
                                                                                                   version, timeout))
            time.sleep(5)

        if correct:
            pass
        else:
            raise ValueError("Expected version {}. Server reports {}.".format(expected_version, version))

    @staticmethod
    def unpack(parser, archive, target):
        target_dir = os.path.abspath(target)
        os.makedirs(target_dir, exist_ok=True)

        util.unzip(archive, target_dir)


class GenericFunctions:
    @staticmethod
    def cd(parser, folder):
        os.chdir(folder)

    @staticmethod
    def pushd(parser, folder):
        parser.dirstack.append(os.getcwd())
        os.chdir(folder)

    @staticmethod
    def popd(parser):
        try:
            os.chdir(parser.dirstack.pop())
        except IndexError:
            raise IndexError("No folder left on stack to pop into.")

    @staticmethod
    def zip(parser, folder, zipname):
        util.make_zip(zipname, os.path.join(os.getcwd(), folder), os.getcwd())


class Parser:
    """
    Class for parsing Webstore Manager commands in script mode. See HTML documentation for details.
    """

    functions = {  # Mapping of function names to actual python functions.
        'cd': GenericFunctions.cd,
        'pushd': GenericFunctions.pushd,
        'popd': GenericFunctions.popd,
        'chrome.init': ChromeFunctions.init,
        'chrome.setapp': ChromeFunctions.set_app,
        'chrome.new': ChromeFunctions.new,
        'chrome.update': ChromeFunctions.update,
        'chrome.publish': ChromeFunctions.publish,
        'chrome.check_version': ChromeFunctions.check_version,
        'chrome.unpack': ChromeFunctions.unpack,
        'zip': GenericFunctions.zip
    }

    def __init__(self, script=None, script_fn=None):
        """ Initialize Parser with one and only one of script as string or script in a file. """
        super().__init__()
        if (not script and not script_fn) or (script and script_fn):
            raise ValueError("One of script or script_fn must be set!")

        if script_fn:
            self.script = open(script_fn).readlines()
        else:
            self.script = script

        self.variables = {}
        self.dirstack = []

        self.patterns = {
            'variable': re.compile(r'\s*\$\{([^}]+)\}\s*'),  # pattern of '  ${varname}  '
        }

    def execute(self):
        """
        Execute the script of this parser. Main function.
        Returns:
            None.
        """
        for line in self.script:
            self.execute_line(line)

    def execute_line(self, line: str):
        """ Execute a single line (i.e. one command). """
        line = line.strip()

        if not line or line.startswith("#"):
            logger.debug("Skipping line: {}".format(line))
            return

        logger.debug("Executing line: {}".format(line))

        tokens = line.split()
        tokens = self.resolve_variables(tokens)

        logger.debug("  tokens: {}".format(tokens))

        # if assignment, process it. If not, call it as a function
        if not self.process_assignment(tokens):
            func = self.token_to_func(tokens[0])
            func(self, *tokens[1:])

    def token_to_func(self, token):
        """
        Convert a token into a function object, if such mapping exists.
        Args:
            token(str): Token to convert.

        Returns:
            Function corresponding to the token.

        Raises:
            FunctionNotDefinedException: if no mapping between the token and function exists.
        """
        try:
            logger.debug("  Trying to parse token {} as a function".format(token))
            return self.functions[token]
        except KeyError:
            raise FunctionNotDefinedException(token)

    def resolve_variables(self, tokens):
        """
        Expand all variables in the given tokens.

        Variables are any tokens that have the form of ${name}.

        Args:
            tokens(list of str): List of tokens to expand.

        Returns:
            A new list of tokens, in which all variables have been expanded.
        """
        res = []
        for token in tokens:
            res.append(self.resolve_variable(token))

        return res

    def resolve_variable(self, token: str):
        """
        Expand a variable. If a given token is not a variable, just return it.

        Args:
            token: Token to try and expand.

        Returns:
            str: Expanded value of the token if it was a variable or its original content if it was not.

        Raises VariableNotDefinedException: If a given token was a variable, but it had no assigned value.
        """
        match = re.match(self.patterns['variable'], token)
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

            return value
        else:  # token is not a variable, just return it
            return token

    def process_assignment(self, tokens):
        """
        Process a line as a value assignment.

        Updates internally stored variables of the Parser object. They are accessible in the variables field.

        Args:
            tokens(list of str): List of tokens to process.

        Returns:
            True if the list of tokens was a valid assignment, False otherwise.

        """
        if '=' in tokens:
            if not len(tokens) == 3:
                raise ValueError("Assignment has to be 'var = value'. Parsed tokens: {}".format(tokens))

            left = tokens[0]
            right = tokens[2]
            self.variables[left] = right
            logger.debug("  Assigning {} <- {}".format(left, right))
            return True
        else:
            return False


class VariableNotDefinedException(Exception):
    pass


class FunctionNotDefinedException(Exception):
    pass


class InvalidStateException(Exception):
    pass
