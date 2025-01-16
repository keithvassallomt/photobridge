from pathlib import Path
from subprocess import Popen, PIPE

DATA_LOCATION: Path = Path.home() / "Library" / "Application Support" / "PhotoBridge"


def run_applescript(script: str, *args) -> tuple[int, str, str]:
    """
    Runs an AppleScript script.

    :param script: the script to run.
    :param args: a list of arguments to send to the script.

    :returns:

        - return_code (:py:class:`int`) - the script's return code.
        - stdout (:py:class:`str`) - standard output from the script.
        - stderr (:py:class:`str`) - standard error from the script.

    """
    arguments = list(args)
    p = Popen(['osascript', '-'] + arguments, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = p.communicate(script)
    return p.returncode, stdout, stderr


def temp_folder() -> Path:
    """
    Get the location of the ``tmp`` folder within TaskBridge's Application Data folder.

    :return: path to the ``tmp`` folder.
    """
    tmp_folder = DATA_LOCATION / 'tmp/'
    tmp_folder.mkdir(parents=True, exist_ok=True)
    return tmp_folder


def data_location() -> Path:
    """
    Get the location where PhotoBridge stores files.
    :return: the location of the Application Support folder for PhotoBridge
    """
    return DATA_LOCATION