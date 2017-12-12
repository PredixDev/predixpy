
# PredixPy

The Predix Python SDK has been crafted to help Python developers have quick
success writing applications using Predix Services.

Install it from PyPI:

```
pip install predix
```

If that isn't working for you, we highly recommend [The Hitchiker's Guide to
Properly Installing Python][hitchiker] to learn about installing `python`,
`pip`, and `virtualenv` for your environment.  For industrial environments, you
may also need to learn how to set your proxies.

See the [Predix Volcano App][volcanoapp] for a full demonstration of the SDK
used in a Python Flask App.

# Getting Started

Please see the [Getting Started Guide][gettingstarted] for a walkthrough and
introduction to basic usage of the Python SDK.  The following services are
already supported for **Python 2.7.x**.  Verification of compatibility with
**Python 3.6.x** is on the near-term roadmap.

- [x] [User Account and Authentication][uaa] (UAA)
- [x] [Predix Asset][asset]
- [x] [Predix Time Series][timeseries]
- [x] [Predix Access Control][acs] (ACS)
- [x] [Blob Store][blobstore]
- [x] [Logging][logging]
- [x] Weather (Deprecated)
- more...

# Getting Help

If something doesn't work as expected and you want help:

- Create a [GitHub Issue][github] in this project
- Ask on the [Predix Developer Forum][forum]
- Send email to volcano@ge.com and we'll respond as soon as we can

# Contributors

See the [Developing PredixPy Guide][devguide] if you want to contribute or
modify the SDK itself.  If you send a PR it will be reviewed as soon as
possible but contribution guidelines for external parties may require
additional discussion.

---
[catalog]: https://www.predix.io/catalog/services
[hitchiker]: http://docs.python-guide.org/en/latest/starting/installation/
[forum]: https://forum.predix.io/index.html
[github]: https://github.com/PredixDev/predixpy/issues
[uaa]: https://predixpy.run.aws-usw02-pr.ice.predix.io/services/index.html#user-accounts-and-authentication
[timeseries]: https://predixpy.run.aws-usw02-pr.ice.predix.io/services/index.html#time-series
[asset]: https://predixpy.run.aws-usw02-pr.ice.predix.io/services/index.html#asset
[acs]: https://predixpy.run.aws-usw02-pr.ice.predix.io/services/index.html#access-control
[blobstore]: https://predixpy.run.aws-usw02-pr.ice.predix.io/services/index.html#blob-store
[logging]: https://predixpy.run.aws-usw02-pr.ice.predix.io/services/index.html#logging
[gettingstarted]: https://predixpy.run.aws-usw02-pr.ice.predix.io/getting-started/index.html
[devguide]: https://predixpy.run.aws-usw02-pr.ice.predix.io/devguide/index.html
[volcanoapp]: https://github.com/PredixDev/predix-volcano-app

[![Analytics](https://ga-beacon.appspot.com/UA-82773213-1/predixpy/readme?pixel)](https://github.com/PredixDev)
