import boto3
session = boto3.Session(profile_name="profile_name_here",region_name="eu-west-1")
client = session.client('iam')
response = client.list_users()

# Iterate over the response to print usernames
for user in response['Users']:
    user_name = user['UserName']  # Assign the username to user_name variable
    # print(user_name)  # Print the username
    # For excluding users
    if user_name == "<excluding_user_name>":
        continue
    else:
        # Now you can use user_name to list access keys for each user
        access_keys_response = client.list_access_keys(UserName=user_name)

        # Iterate over access keys metadata and extract creation date
        for access_key in access_keys_response['AccessKeyMetadata']:
            Create_Date = access_key['CreateDate']
            User_Name = access_key['UserName']
            print("UserName \t\t\t\t\t Creation_Date")
            print("---------------------------------------------------")
            print(User_Name,  "\t\t",  Create_Date)