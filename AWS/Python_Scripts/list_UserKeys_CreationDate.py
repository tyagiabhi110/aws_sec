import boto3

# Debug on/off

DEBUG = 0

from datetime import date

today = date.today()
print("Today's date:", today)
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
        except ClientError as e:
                print("e")