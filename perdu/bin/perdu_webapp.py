#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Perdu webapp.

Usage:
  perdu_webapp [--port=<port>] [--localhost]
  perdu_webapp -h | --help
  perdu_webapp --version

Options:
  --localhost   Only allow connections from this computer.
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt
from perdu.webapp import perdu_app
import os


def main():
    args = docopt(__doc__, version="Perdu webapp 1.0")
    port = int(args.get("--port", False) or 5000)
    host = "localhost" if args.get("--localhost", False) else "0.0.0.0"

    print("perdu webapp started on {}:{}".format(host, port))

    perdu_app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    main()
