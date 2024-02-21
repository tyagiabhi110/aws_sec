import boto3

# Debug on/off

DEBUG = 0

with open("../accounts.txt") as accounts:
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
                        creation_time = key['CreateDate']
                        username = key['UserName']
                        print("User Name \t\t\t\t Access_Key_Creation_Date")
                        print("---------------------------------------------------")
                        print(username, "\t\t", creation_time)
        except ClientError as e:
                print("e")
