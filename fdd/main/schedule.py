"""
Usage: python schedule.py < input

See README.md for input format
"""

from absl import app

from .. import log

def _main(_argv):
    log.init()

    log.info("Hello, World")


if __name__ == "__main__":
    app.run(_main)
