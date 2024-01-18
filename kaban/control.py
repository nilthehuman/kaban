import argparse
import textwrap
from pathlib import Path


from kaban.config import KabanConfig
from kaban.data import KabanData
from kaban.defaults import *


# these could be macros except Python has no macros
def _unknown_command(args):
    print(f"I don't think '{args.command}' is a valid command to be honest.")
    print("Take a look at 'kaban help' if you need a list of commands.")
    raise ValueError

def _unexpected_object(args):
    print(f"Not sure what you mean by '{args.object}'.")
    print(f"Check out 'kaban help {args.command}' for a list of options.")
    raise ValueError

def _unknown_option(args):
    print(f"'{args.options}' doesn't look like a valid set of options.")
    print(f"'kaban help {args.command}' will hook you up if you need a refresher.")
    raise ValueError


class KabanControl:
    """Main class responsible for core data operations requested by the user."""

    def __init__(self, data=None):
        # parse command line arguments to see what the user wants to do
        argparser = argparse.ArgumentParser()
        argparser.add_argument('command', metavar='command', type=str)
        # can't mark positional arguments as required=False :(
        argparser.add_argument('object', metavar='object', type=str)
        # --config is special in that it is the only option not represented in the config file
        argparser.add_argument('--config', type=str)
        argparser.add_argument('--local', action='store_true')
        argparser.add_argument('--merge', action='store_true')
        argparser.add_argument('--quiet', action='store_true')
        # thanks but we will print the help manually instead
        argparser.print_help = self.help
        argparser.print_usage = self.help
        argparser.error = lambda _: ()
        # go ahead and parse command line arguments
        self.args = argparser.parse_args()

        # find and read kaban config file
        self.config = KabanConfig()
        try:
            self.config.load_from_file(filename=self.args.config)
        except FileNotFoundError:
            pass  # just use the default config
        self.data = KabanData()
        # load tasks from a YAML or TOML file if there already is one
        try:
            self.data.load_from_file(filename=TOML_FILE_PATH, format='toml')
        except FileNotFoundError:
            try:
                self.data.load_from_file(filename=YAML_FILE_PATH, format='yaml')
            except FileNotFoundError:
                # guess we have a clean slate then: kaban init is yet to be run;
                # let's TypeError on any subsequent data operation
                self.data = None

    def _execute_command(self):
        """Find out what command the user wants to run and call the corresponding method"""
        assert self.args is not None
        try:
            command_method = getattr(self, self.args.command)
        except AttributeError:
            try:
                _unknown_command(self.args)
            except ValueError:
                return False
        except TypeError:
            self.help()
            return False
        assert command_method
        try:
            return command_method(self.args)
        except ValueError:
            return False

    def init(self, args=None):
        """kaban init [--dir=DIR] [--local]
        Initialize git repo in ~/.kaban/, create and commit empty TOML file
        --dir=DIR \tCreate git repository in DIR instead
        --local   \tTurn off autopush and keep task data only on this machine
        See also 'kaban help autopush'.
        """
        if args.object is not None:
            _unexpected_object(args)
        # create ~/.kaban/ directory
        Path.mkdir(KABAN_DIR, exist_ok=True)
        # create empty TOML file
        Path.touch(TOML_FILE_PATH)
        # create default config file
        self.config.save_to_file(filename=CONFIG_FILE_PATH)
        return True

    def config(self, args=None):
        """kaban config [--dir=DIR] [--local]
        Manage persistent user settings to customize kaban's behavior
        format    \tSpecify the data serialization format kaban uses to store your data

        quiet     \tTell kaban to stfu and print messages only in response to query commands such as 'show' or 'status'
        """
        if args.object is not None:
            _unexpected_object(args)
        # create default toml file in ~/.kaban/
        return True

    def help(self, args=None):
        """kaban help [COMMAND]
        Print a help message about a specific command or about general usage
        [COMMAND] \tSpecific kaban command you want to know more about
        """
        def dedent(string):
            nonempty_lines = [line for line in string.split('\n') if line and not line.isspace()]
            return textwrap.dedent('\n'.join(nonempty_lines))
        if args is None or args.object is None:
            helptext = """
                What's up, this is kaban 0.1.0, your favorite command line task manager,
                reporting for duty. Use the following commands to handle your tasks and todos:
                """
            helptext = dedent(helptext)
            # collect docstrings of all KabanControl methods
            for methodname in dir(self):
                if methodname[0] != '_':
                    method = getattr(self, methodname)
                    if callable(method) and method.__doc__ is not None:
                        # actually a method as opposed to a variable
                        docstring_second_line = method.__doc__.split('\n')[1].strip()
                        helptext += '\n  ' + methodname + '  \t' + docstring_second_line
            print(helptext)
        else:
            # the user seems to want info on a specific command
            try:
                method = getattr(self, args.object)
                if not callable(method):
                    raise AttributeError
                usage, _, docstring_tail = method.__doc__.partition('\n')
                print(usage)
                further_helptext = '\n'.join(['  ' + line for line in dedent(docstring_tail).split('\n')])
                print(further_helptext)
            except AttributeError:
                _unexpected_object(args)
            except ValueError:
                return False
        return True


def main():
    control = KabanControl()
    success = control._execute_command()
    exit(int(not success))


if __name__ == "__main__":
    main()

