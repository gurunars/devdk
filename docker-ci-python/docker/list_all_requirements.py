import sys

from yaml import load


with open(sys.argv[1]) as fil:
    data = load(fil.read())
    for reqs in ["install_requires", "setup_requires", "tests_require"]:
        for req in data.get(reqs, []):
            print(req, end=' ')
