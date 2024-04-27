import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import concurrent.futures

def get_all_roles(client):
    roles = []
    paginator = client.get_paginator('list_roles')
    for page in paginator.paginate():
        roles.extend(page['Roles'])
    return roles

def roles_last_used(role_name):
    try:
        my_session = boto3.session.Session(profile_name="IAMUERReadOnly", region_name='eu-west-1')
        client = my_session.client('iam')
        response = client.get_role(RoleName=role_name)["Role"]
        last_used_date_str = response['RoleLastUsed'].get('LastUsedDate')
        if last_used_date_str is not None:
            last_used_date = last_used_date_str.replace(tzinfo=None)
            days_since_last_used = (datetime.utcnow() - last_used_date).days
            if days_since_last_used > 30:
                print(f"Role '{role_name}' was last used {days_since_last_used} days ago.")
                return True  # Role meets the criteria
        else:
            print(f"Role '{role_name}' has never been used.")
            return True  # Role meets the criteria

    except ClientError as e:
        print(e)
    return False  # Role does not meet the criteria

def process_roles(role_names):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(roles_last_used, role_names)
    return list(results)  # Convert the results to a list

def main():
    try:
        my_session = boto3.session.Session(profile_name="IAMUERReadOnly", region_name='eu-west-1')
        client = my_session.client('iam')

        # Get all roles using pagination
        all_roles = get_all_roles(client)

        # Filter roles starting with 'AWSReservedSSO'
        reserved_sso_roles = [role['RoleName'] for role in all_roles if role['RoleName'].startswith('AWSReservedSSO')]
        not_reserved_sso_roles = [role['RoleName'] for role in all_roles if not role['RoleName'].startswith('AWSReservedSSO')]

        print(f"Total number of roles identified: {len(all_roles)}")
        print(f"Total number of roles not started with 'AWSReservedSSO': {len(not_reserved_sso_roles)}")
        print("Roles not started with 'AWSReservedSSO':")
        for role_name in not_reserved_sso_roles:
            print(role_name)

        total_reserved_sso_roles = len(reserved_sso_roles)
        print(f"Total number of roles started with 'AWSReservedSSO': {total_reserved_sso_roles}")

        # Process roles concurrently and get results
        results = process_roles(reserved_sso_roles)

        total_unused_reserved_sso_roles = sum(results)
        print(f"Total number of roles started with 'AWSReservedSSO' not used for more than 30 days (including never used): {total_unused_reserved_sso_roles}")

    except ClientError as e:
        print(e)

if __name__ == "__main__":
    main()
