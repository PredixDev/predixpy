import logging
import predix.admin.cf.orgs

logging.basicConfig(level=logging.DEBUG)

my_org = predix.admin.cf.orgs.Org()

my_org.add_user(user_name="m4rk.odell@gmail.com")
