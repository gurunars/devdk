from dict_validator.fields import String
from dict_validator import Dict


class GitCredentials:
    ssl_key = String()


class GitProject:
    url = String()


class PkgRepo:
    url = String()


class PkgRepoCredentials:
    username = String()
    password = String()


class StoredConfig:
    pkg_repo = Dict(PkgRepo)
    git_project = Dict(GitProject)


class IgnoredConfig:
    git_credentials = Dict(GitCredentials)
    pkg_repo_credentials = Dict(PkgRepoCredentials)
