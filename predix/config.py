
import os
import logging

def is_cf_env():
    return ('VCAP_SERVICES' in os.environ) or ('VCAP_APPLICATION' in os.environ)

def get_env_key(obj, key=None):
    """
    Return environment variable key to use for lookups within a
    namespace represented by the package name.

    For example, any varialbes for predix.security.uaa are stored
    as PREDIX_SECURITY_UAA_KEY
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

def set_env_value(obj, attribute, value):
    """
    Set the environment variable value for the attribute of the
    given object.

    For example, `set_env_value(predix.security.uaa, 'uri', 'http://...')`
    will set the environment variable PREDIX_SECURITY_UAA_URI to the given
    uri.
    """
    varname = get_env_key(obj, attribute)
    os.environ[varname] = value
    return varname
