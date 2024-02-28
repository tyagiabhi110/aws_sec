#############################################################################################################
#
# Author - Abhishek Tyagi
# Purpose - undertake various user admin activities
#              - chase people with passwords needing resets
#              - chase non mfa setup
#
# No arguments
#
# Program Flow
#  - Open up session to the user account and create a client to be used in later code
#  - Look up password expiry on users and email users who will need to update their password in the next 14 days
#      - get credentials report
#      - loop through credentials report
#      - work out how many days left before password expiry and compare to GRACE PERIOD
#      - email user to update password
#      - log fact user has been emailed
#  - Look up the MFA set against a user account and email them if it does not exist
#      - List users
#      - check if user has console password (checks if real user)
#      - check mfa for user
#      - email user to reset mfa
#
#  - Lambda runs daily
#
#############################################################################################################

# Imports
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
import json
import csv
from time import sleep
import datetime
import dateutil.parser

# Debug on/off

DEBUG = 0

# Variables

GRACE_PERIOD = 14
region = "eu-west-1"
SEND_EMAIL = True
FROM_ADDRESS = "aws_sec.operations@<org_name>.com"
EXPLANATION_FOOTER = "TO UPDATE YOUR ACCOUNT PLEASE LOGIN AS PER NORMAL AND ACTION THROUGH THE CONSOLE OR CLI"
EXPLANATION_HEADER = "THIS EMAIL ORGINATED FROM THE <org_name> AWS SYSTEM\n"
password_warn_message = "\n\tYour Password will expire in {} days"  # nosec

# Define a Global String to be the report output sent to ACTION_TOPIC_ARN
REPORT_SUMMARY = ""


# Request the credential report, download and parse the CSV.
def get_credential_report(iam_client):
    resp1 = iam_client.generate_credential_report()
    if resp1['State'] == 'COMPLETE':
        try:
            response = iam_client.get_credential_report()
            credential_report_csv = response['Content'].decode('utf-8')
            reader = csv.DictReader(credential_report_csv.splitlines())
            credential_report = []
            for row in reader:
                credential_report.append(row)
            return (credential_report)
        except ClientError as e:
            print("Unknown error getting Report: " + e)
    else:
        sleep(2)
        return get_credential_report(iam_client)


def days_till_expire(last_changed, max_age):
    # Ok - So last_changed can either be a string to parse or already a datetime object.
    # Handle these accordingly
    if type(last_changed) is str:
        last_changed_date = dateutil.parser.parse(last_changed).date()
    elif type(last_changed) is datetime.datetime:
        last_changed_date = last_changed.date()
    else:
        return -99999
    expires = (last_changed_date + datetime.timedelta(max_age)) - datetime.date.today()
    return (expires.days)


# Query the account's password policy for the password age. Return that number of days
def get_max_password_age(iam_client):
    try:
        response = iam_client.get_account_password_policy()
        return response['PasswordPolicy']['MaxPasswordAge']
    except ClientError as e:
        print("Unexpected error in get_max_password_age: %s" + e)


def email_user(email, message, email_subject):
    if SEND_EMAIL is not True:
        return  # Abort if we're not supposed to send email
    if message == "":
        return  # Don't send an empty message
    client = boto3.client('ses')
    body = EXPLANATION_HEADER + "\n" + message + "\n\n" + EXPLANATION_FOOTER
    try:
        client.send_email(
            Source=FROM_ADDRESS,
            Destination={'ToAddresses': [email, "aws_sec.operations@<org_name>.com"]},
            Message={
                'Subject': {'Data': email_subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        print("Email Sent to {}".format(email))
        return
    except ClientError as e:
        print("Failed to send message to {}: {}".format(email, e))
        # ACTION_SUMMARY = ACTION_SUMMARY + "\nERROR: Message to {} was rejected: {}".format(email, e.message)


# Get Master AWS account id
def get_MasterId():
    MasterId = boto3.client('sts').get_caller_identity().get('Account')
    return MasterId


def lambda_handler(event, context):

    global REPORT_SUMMARY

    email_subject_pwd = "Credential Expiration Notice from AWS Sec Team"  # nosec
    email_subject_mfa = "AWS MFA Login Requirement from AWS SEC Team"  # nosec

    # Get accounts data
    UserAccount = "<Enter User Account ID>"

    print("****************************************")
    print("Commencing user admin tasks")
    print("****************************************")

    try:
        ###########################################################
        #
        # Connect to target account
        #
        ###########################################################

        print("****************************************")
        print("Making connection")
        print("****************************************")

        session = boto3.Session(region_name=region)
        # create an STS client object that represents a live connection to the
        # STS service
        sts_client = session.client('sts')
        # print(sts_client.get_caller_identity())
        # Call the assume_role method of the STSConnection object and pass the role
        # ARN and a role session name.
        RoleArn = "arn:aws:iam::" + UserAccount.rstrip('\n') + ":role/OrganizationAccountAccessRole"
        # print(RoleArn)
        assumed_role_object = sts_client.assume_role(
            RoleArn=RoleArn,
            RoleSessionName="UserAdminTask"
        )
        # print(assumed_role_object)

        # From the response that contains the assumed role, get the temporary
        # credentials that can be used to make subsequent API calls
        credentials = assumed_role_object['Credentials']

        assume_session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
            region_name=region.rstrip('\n').rstrip()
            )
        # assume_sts_client = assume_session.client('sts')
        # print(assume_sts_client.get_caller_identity())

        iam_client = assume_session.client(service_name="iam")

    except ClientError as err:
        print("\nClient Error = %s" % err)
    except NoCredentialsError as err:
        print("\nCredentials Error = %s" % err)
    except Exception as err:
        print("\nError = %s" % err)

    ###########################################################
    #
    # Chase users with password reset required
    #
    ###########################################################

    print("****************************************")
    print("Commencing check on passwords coming up to expiry")
    print("****************************************")

    try:
        max_age = get_max_password_age(iam_client)
        print(max_age)
        credential_report = get_credential_report(iam_client)
        # Iterate over the credential report, use the report to determine password expiration
        for row in credential_report:
            if row['password_enabled'] != "true":
                continue  # Skip IAM Users without passwords, they are service accounts

            message = ""  # This is what we send to the user

            password_expires = days_till_expire(row['password_last_changed'], max_age)
            print(row)
            print(password_expires)
            if password_expires > 0:
                if password_expires < GRACE_PERIOD:
                    message = message + "Dear User\n" + password_warn_message.format(password_expires) + ".\n\nAWS SEC Team\n"
                    REPORT_SUMMARY = REPORT_SUMMARY + "\n{}'s Password Will expire in {} days".format(row['user'], password_expires)
                    email_user(row['user'], message, email_subject_pwd)

        print(REPORT_SUMMARY)

    except ClientError as err:
        print("\nClient Error = %s" % err)
    except NoCredentialsError as err:
        print("\nCredentials Error = %s" % err)
    except Exception as err:
        print("\nError = %s" % err)

    ###########################################################
    #
    # Chase users with MFA required
    #
    ###########################################################

    print("****************************************")
    print("Commencing check on users without mfa")
    print("****************************************")

    try:
        # Setup pagination to handle variable number of users
        paginator = iam_client.get_paginator('list_users')
        response_iterator = paginator.paginate(PaginationConfig={'PageSize': 100})
        for page in response_iterator:
            message = ""
            print("Next Page : {} ".format(page['IsTruncated']))
            u = page['Users']
            for user in u:
                if user['UserName'].rstrip() == "AWSBuildUser":
                    print("Skipping AWSBuildUser")
                elif user['UserName'].rstrip() == "AWSSEC.CredentialReport@<org_name>.com":
                    print("Skipping DownloadUserCredentialReport")
                else:
                    response = iam_client.list_mfa_devices(
                        UserName=user['UserName']
                    )
                    if len(response['MFADevices']) == 0:
                        print(user['UserName'] + " has no MFA")
                        message = "Dear User \n\nYou do not have MFA enabled on your AWS account.\n\nPlease action this as a matter of urgency.\n\nAWS SEC Team"
                        email_user(user['UserName'], message, email_subject_mfa)

    except ClientError as err:
        print("\nClient Error = %s" % err)
    except NoCredentialsError as err:
        print("\nCredentials Error = %s" % err)
    except Exception as err:
        print("\nError = %s" % err)

    print("****************************************")

    # Return
    return {
        'statusCode': 200,
        'body': json.dumps('Accounts Configuration Complete')
    }
