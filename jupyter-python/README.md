# jupyter-python

A docker image that allows you to use Kotlin instead of Python.

See [example](./Example.ipynb) for more details

## Requirements

- UNIX
- Docker

## Usage

1\. Create and enter a project directory:

    mkdir notebook_project
    cd notebook_project

2\. Create a `notebook.sh` script for simplicity:

    cat > ./notebook.sh <<DELIM
    #!/bin/sh
    set -e
    docker run -it --rm \\
        -v \$HOME/.jupyter/\$PWD:/home/jupyter/.m2 \\
        -v \$PWD:/project \\
        -p 8888:8888 \\
        nephilimsolutions/jupiter-python
    DELIM

    chmod +x notebook.sh

3\. Run using the script:

    ./notebook.sh

4\. Open [<http://localhost:8888>](http://localhost:8888) in a browser.
