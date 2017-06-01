
import predix.admin.cf.api
import predix.admin.cf.spaces


class App(object):
    """
    Operations and data for Cloud Foundry Apps.
    """
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.api = predix.admin.cf.api.API()
        self.space = predix.admin.cf.spaces.Space()

    def get_app_guid(self, app_name):
        """
        Returns the GUID for the app instance with
        the given name.
        """
        summary = self.space.get_space_summary()
        for app in summary['apps']:
            if app['name'] == app_name:
                return app['guid']

    def delete_app(self, app_name):
        """
        Delete the given app.

        Will fail intentionally if there are any service
        bindings.  You must delete those first.
        """
        if app_name not in self.space.get_apps():
            logging.warn("App not found so... succeeded?")
            return True

        guid = self.get_app_guid(app_name)
        self.api.delete("/v2/apps/%s" % (guid))
