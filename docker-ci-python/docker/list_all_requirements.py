import sys

from yaml import load


with open(sys.argv[1]) as fil:
    YAML = load(fil.read())


print(" ".join(
    YAML.get("install_requires", []) +
    YAML.get("setup_requires", []) +
    YAML.get("tests_require", [])
))