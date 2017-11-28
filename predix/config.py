
import os
import logging

def get_env_key(obj, key=None):
    """
    Return environment variable key to use for lookups within a
    namespace represented by the package name.
    """
    return str.join('_', [obj.__module__.replace('.','_').upper(),
        key.upper()])

def get_env_value(obj, attribute):
    """
    Returns the environment variable value for the attribute of
    the given object.

    For example `get_env_value(predix.security.uaa, 'uri')` will
    return value of environment variable PREDIX_SECURITY_UAA_URI.

    """
    varname = get_env_key(obj, attribute)
    var = os.environ.get(varname)
    if not var:
        raise ValueError("%s must be set in your environment." % varname)

    return var
