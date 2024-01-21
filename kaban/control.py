import argparse
import configparser
import re
import textwrap
from pathlib import Path


import git


from kaban.config import KabanConfig
from kaban.data import KabanData
from kaban.defaults import *
from kaban.version import get_version


# these could be macros except Python has no macros
def _unknown_command(args):
    print(f"I don't think `{args.command}` is a valid command to be honest.")
    print("Take a look at `kaban help` if you need a list of commands.")
    raise ValueError

def _unexpected_object(args):
    print(f"Not sure what you mean by '{args.object}'.")
    print(f"Check out `kaban help {args.command}` for a list of options.")
    raise ValueError

def _unknown_options(args):
    print(f"Sorry, I don't recognize these options: '{' '.join(args.further_args)}'.")
    print(f"`kaban help {args.command}` will hook you up if you need a refresher.")
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
        self.args, further_args = argparser.parse_known_args()
        self.args.further_args = further_args

        # find and read kaban config file
        self.config_object = KabanConfig()
        try:
            self.config_object.load_from_file(filename=self.args.config)
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
            return command_method()
        except ValueError:
            return False

    def init_done(self):
        """Has `kaban init` been run yet?"""
        if not Path.exists(TOML_FILE_PATH):
            return False
        if self.args.local or self.config_object.local:
            return True
        else:
            try:
                if git.Repo(KABAN_DIR):
                    return True
            except git.exc.InvalidGitRepositoryError:
                return False

    def get_creds(_self):
        """Has the user provided their username and access token for the remote?"""
        try:
            url = git.Repo(KABAN_DIR).config_reader().get_value('remote "origin"', 'url')
        except (configparser.NoOptionError, configparser.NoSectionError):
            return None
        # try for 'https://user:token@github.com/user/myrepo.git'
        match = re.fullmatch(r'(\w+://)?(\w+):(gh._\w+)@[\w\./]+', url)
        if match is not None:
            user = match.group(2)
            token = match.group(3)
            return user, token
        # maybe 'https://user@github.com/user/myrepo.git' with no token?
        match = re.fullmatch(r'(\w+://)?(\w+)@[\w\./]+', url)
        if match is not None:
            user = match.group(2)
            return (user)
        return None

    def no_object(method):
        def check_object(self):
            if self.args.object is not None:
                _unexpected_object(self.args)
            else:
                return method(self)
        # make sure the wrapper inherits the docstring
        check_object.__doc__ = method.__doc__
        return check_object

    def no_further_args(method):
        def check_further_args(self):
            if self.args.further_args:
                _unknown_options(self.args)
            else:
                return method(self)
        # make sure the wrapper inherits the docstring
        check_further_args.__doc__ = method.__doc__
        return check_further_args

    def with_init(method):
        def check_init(self):
            if self.init_done():
                return method(self)
            else:
                print(f"No kaban repo found at '{KABAN_DIR}'.")
                print("Pretty sure you need to run `kaban init` first.")
                return False
        # make sure the wrapper inherits the docstring
        check_init.__doc__ = method.__doc__
        return check_init

    def not_local(method):
        def check_local(self):
            if self.args.local or self.config_object.local:
                print("Uh, that command is not available in local mode.")
                print("You might want to go `kaban config local false` first.")
            else:
                return method(self)
        # make sure the wrapper inherits the docstring
        check_local.__doc__ = method.__doc__
        return check_local

    def with_remote(method):
        def check_remote(self):
            try:
                git.Repo(KABAN_DIR).config_reader().get_value('remote "origin"', 'url')
            except (configparser.NoOptionError, configparser.NoSectionError):
                print(f"No remote URL found in the git config of the '{KABAN_DIR}' repo.")
                print("We can fix that right now with `kaban remote URL`, just say the word.")
                return False
            return method(self)
        # make sure the wrapper inherits the docstring
        check_remote.__doc__ = method.__doc__
        return check_remote

    def with_creds(method):
        def check_creds(self):
            if self.get_creds() is None:
                print(f"No credentials found in the git config of the '{KABAN_DIR}' repo.")
                print("Just say `kaban user USERNAME` and `kaban token TOKEN` when you're ready.")
                return False
            else:
                return method(self)
        # make sure the wrapper inherits the docstring
        check_creds.__doc__ = method.__doc__
        return check_creds

    @no_object
    @no_further_args
    def init(self):
        """kaban init [--dir=DIR] [--local]
        Initialize git repo in ~/.kaban/, create and commit empty TOML and config file
        --dir=DIR \tCreate git repository in DIR instead
        --local   \tKeep task data only on this machine
        See also `kaban help config`.
        """
        if self.init_done():
            print(f"Relax, you already have a kaban repo at '{KABAN_DIR}'.")
            return True
        # create ~/.kaban/ directory
        Path.mkdir(KABAN_DIR, exist_ok=True)
        # create empty TOML file
        Path.touch(TOML_FILE_PATH)
        # create default config file
        self.config_object.save_to_file(filename=CONFIG_FILE_PATH)
        # initialize local git repo and create first commit
        kaban_repo = git.Repo.init(KABAN_DIR)
        # not kaban_repo.git.add(all=True) because the user might want to keep
        # other files we don't want to track in the same directory
        kaban_repo.index.add([TOML_FILE_PATH, CONFIG_FILE_PATH])
        kaban_repo.index.commit("Init kaban repo")
        assert not kaban_repo.is_dirty()
        print(f"New kaban repo founded at '{KABAN_DIR}'. Let's do this!")
        if self.args.local:
            print("Just a heads up: this repo will *not* be synced to GitHub unless you provide")
            print("your GitHub credentials and say `kaban autopush`.")
        else:
            print("(Don't forget to run `kaban remote GIT_URL` to enable syncing.)")
        return True

    @no_further_args
    @with_init
    @not_local
    def remote(self):
        """kaban remote [URL]
        Set or print the full git URL to upload changes to including credentials
        URL       \tThe URL of a host you have push access to
        """
        if self.args.object is not None:
            with git.Repo(KABAN_DIR).config_writer() as git_config:
                git_config.set_value('remote "origin"', 'url', self.args.object).release()
            print(f"Remote URL set to '{self.args.object}'.")
        else:
            try:
                print(git.Repo(KABAN_DIR).config_reader().get_value('remote "origin"', 'url'))
            except (configparser.NoOptionError, configparser.NoSectionError):
                print("No remote URL has been set.")
                return False
        return True

    @no_object
    @no_further_args
    @with_init
    @with_remote
    def cred(self):
        """kaban cred
        Check if username and access token have been included in the remote URL
        See also `kaban help user` and `kaban help token`.
        """
        creds = self.get_creds()
        if creds is None:
            print("It looks like you haven't provided any credentials yet.")
            print("See `kaban help user` and `kaban help token` about that.")
            return False
        try:
            print(f"Remote username: {creds[0]}")
            print(f"Remote access token: {creds[1]}")
        except IndexError:
            print("Sorry, your access token is still missing.")
            return False
        return True

    @no_further_args
    @with_init
    @with_remote
    def user(self):
        """kaban user USERNAME
        Set username for remote repo authentication
        USERNAME \tThe username you use to access the remote
        See also `kaban help token`.
        """
        username = self.args.object
        # TODO: turn this into a decorator too?
        if not username:
            print("You seem to be missing the USERNAME argument.")
            print("See `kaban help user` for wisdom and clarity.")
            return False
        kaban_repo = git.Repo(KABAN_DIR)
        url = kaban_repo.config_reader().get_value('remote "origin"', 'url')
        new_url = None
        # is an old username already present?
        match = re.fullmatch(r'(\w+://)?\w+(:gh._\w+)?@([\w\./]+)', url)
        if match is not None:
            scheme_prefix = match.group(1) if match.group(1) else ''
            access_token = match.group(2) if match.group(2) else ''
            host_and_path = match.group(3)
            new_url = scheme_prefix + username + access_token + '@' + host_and_path
        # no credentials given yet
        else:
            match = re.fullmatch(r'(\w+://)?([\w\./]+)', url)
            if match is not None:
                scheme_prefix = match.group(1) if match.group(1) else ''
                host_and_path = match.group(2)
                new_url = scheme_prefix + username + '@' + host_and_path
        if new_url is not None:
            with kaban_repo.config_writer() as git_config:
                git_config.set_value('remote "origin"', 'url', new_url).release()
            print(f"Remote username set to '{username}'. Welcome aboard!")
            return True
        print("Failed, something's fishy here. Are you sure your remote URL is well-formed?")
        return False

    @no_further_args
    @with_init
    @with_remote
    def token(self):
        """kaban token TOKEN
        Set access token for remote repo authentication
        TOKEN    \tA personal access token with read and write permissions
        WARNING: you are strongly advised to use a fine-grained token constrained
        to this one repository!
        See also `kaban help user`.
        """
        access_token = self.args.object
        # TODO: turn this into a decorator too?
        if not self.args.object:
            print("You seem to be missing the TOKEN argument.")
            print("See `kaban help token` for wisdom and clarity.")
            return False
        if not re.match(r'gh._', access_token):
            # token format is suspicious
            print("Warning: your access token doesn't seem to start with the conventional 'gh*_' prefix. I hope you know what you're doing.")
        kaban_repo = git.Repo(KABAN_DIR)
        url = kaban_repo.config_reader().get_value('remote "origin"', 'url')
        new_url = None
        match = re.fullmatch(r'(\w+://)?(\w+)(:gh._\w+)?@([\w\./]+)', url)
        if match is not None:
            scheme_prefix = match.group(1) if match.group(1) else ''
            username = match.group(2)
            host_and_path = match.group(4)
            new_url = scheme_prefix + username + ':' + access_token + '@' + host_and_path
        if new_url is not None:
            with kaban_repo.config_writer() as git_config:
                git_config.set_value('remote "origin"', 'url', new_url).release()
            print(f"Remote access token set. You should be ready to push and sleep well!")
            print("WARNING: you are strongly advised to use a fine-grained token constrained to this one repository!")
            return True
        print("Failed, something's fishy here. Have you set your remote username?")
        return False

    @with_init
    def config(self):
        """kaban config [format FORMAT] [local true/false] [quiet true/false]
        Manage persistent user settings to customize kaban's behavior
        format FORMAT \tSpecify the data serialization format kaban uses to store your data
        local true    \tKeep task data on this machine only, never sync to remote
        quiet true    \tTell kaban to stfu and print messages only in response to query commands such as 'show' or 'status'
        """
        if not self.args.further_args:
            # querying current value
            try:
                value = getattr(self.config_object, self.args.object)
                print(f"Current config value for '{self.args.object}': {value}")
                return True
            except AttributeError:
                _unexpected_object(self.args)
                return False
        else:
            # setting new value
            option_name = self.args.object
            option_type = type(getattr(self.config_object, option_name))
            option_value = self.args.further_args[0]
            if option_type is bool:
                new_value = str(option_value).lower() in ['true', '1']
            else:
                new_value = option_type(option_value)
            setattr(self.config_object, option_name, new_value)
            print(f"'{option_name}' config changed to {new_value}.")
            return True

    @no_further_args
    def help(self):
        """kaban help [COMMAND]
        Print a help message about a specific command or about general usage
        [COMMAND] \tSpecific kaban command you want to know more about
        """
        def dedent(string):
            nonempty_lines = [line for line in string.split('\n') if line and not line.isspace()]
            return textwrap.dedent('\n'.join(nonempty_lines))
        if self.args is None or self.args.object is None:
            helptext = f"""
                What's up, this is kaban {get_version()}, your favorite command line task manager,
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
                method = getattr(self, self.args.object)
                if not callable(method):
                    raise AttributeError
                usage, _, docstring_tail = method.__doc__.partition('\n')
                print(usage)
                further_helptext = '\n'.join(['  ' + line for line in dedent(docstring_tail).split('\n')])
                print(further_helptext)
            except AttributeError:
                _unexpected_object(self.args)
            except ValueError:
                return False
        return True


def main():
    control = KabanControl()
    success = control._execute_command()
    exit(int(not success))


if __name__ == "__main__":
    main()

