import boto3

# Debug on/off

DEBUG = 0

from datetime import date
import optparse
parser = optparse.OptionParser()
today = date.today()
print("Today's date:", today)
def iam_details():
    with open("accounts.txt") as accounts:
        for account in accounts:
            try:
                session = boto3.Session(profile_name=account.rstrip('\n').rstrip(),region_name="eu-west-1")
                print(session)
                client = session.client('iam')
                response = client.list_users()
                for user in response['Users']:
                    user_name= user['UserName']
                    if user_name == "CDOBuildUser":
                        continue
                    else:
                        access_key_response = client.list_access_keys(UserName=user_name)
                        for key in access_key_response["AccessKeyMetadata"]:
                            creation_time = key['CreateDate'].date()
                            username = key['UserName']
                            old_access_key = key['AccessKeyId']
                            #print("User Name \t\t\t\t Access_Key_Creation_Date")
                            #print("---------------------------------------------------")
                            #print(username, "\t\t", creation_time)
                            delta = today - creation_time
                            # print(delta.date())
                            delta_days = delta.days
                            #return parser.parse_args()
                            #return(username, old_access_key, delta_days)
                            yield username, old_access_key, delta_days, creation_time
            except ClientError as e:
                print("e")

def rotation_keys():
    for username, old_access_key, delta_days, creation_time in iam_details():
        if delta_days >= 90:
            print("Key is older than 90 days pls rotate asap for user: ", username)
            print("User Name \t\t\t\t Access_Key_Creation_Date")
            print("---------------------------------------------------")
            print(username, "\t\t", creation_time)
            print("\n")
            print("Generating New Key")
            #new_key = client.create_access_key(UserName=username)
            print("Deleting old key")
            #client.delete_access_key(UserName=username, AccessKeyId=old_access_key)
        else:
            print("Key rotation not required for user: ", username)
            print("\n")
# option, arguments = iam_details()
# rotation_keys(options.username, options.old_access_key, options.delta_days)
iam_details()
rotation_keys()
