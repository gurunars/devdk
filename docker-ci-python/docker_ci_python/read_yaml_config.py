import sys

import yaml

from dict_validator import deserialize, validate, serialize_errors


def read_yaml_config(config_path, config_schema):
    with open(config_path) as fil:
        config = yaml.load(fil.read())
    errors = list(validate(config_schema, config))
    if errors:
        sys.exit(yaml.dump(serialize_errors(errors)))
    return deserialize(config_schema, config)
