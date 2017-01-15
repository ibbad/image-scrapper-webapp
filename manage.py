"""
Main module for managing Telegram application.
"""
import logging
from scrapper import create_app
from flask_script import Manager, Shell

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = create_app('default')
manager = Manager(app)


def make_shell_context():
    """
    Make context for Shell.
    :return: Application models, database and application object.
    """
    return dict(app=app)

manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()