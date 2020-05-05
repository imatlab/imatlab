try:
    import importlib.metadata as _importlib_metadata
except ImportError:
    import importlib_metadata as _importlib_metadata
try:
    __version__ = _importlib_metadata.version("imatlab")
except _importlib_metadata.PackageNotFoundError:
    pass
