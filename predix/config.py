
def get_env_key(obj, key=None):
    """
    Return environment variable key to use for lookups within a
    namespace represented by the package name.
    """
    return str.join('_', [obj.__module__.replace('.','_').upper(),
        key.upper()])
