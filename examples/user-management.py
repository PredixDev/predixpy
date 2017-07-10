import logging
import csv
import predix.admin.cf.orgs

logging.basicConfig(level=logging.DEBUG)

my_org = predix.admin.cf.orgs.Org()

logging.info('Add users from file')
with open('users.csv') as csvUsers:
    reader = csv.DictReader(csvUsers)
    for row in reader:
        logging.debug('Adding user %s as a %s' % (row['username'], row['role']))
        my_org.add_user(user_name=row['username'], role=row['role'])

# logging.info('Remove users from file')
# with open('users.csv') as csvUsers:
#     reader = csv.DictReader(csvUsers)
#     for row in reader:
#         logging.debug('Removing user' + row['username'])
#         my_org.remove_user(user_name=row['username'])
