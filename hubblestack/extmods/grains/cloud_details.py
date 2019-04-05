'''
HubbleStack Cloud Details Grain
'''

import requests


def get_cloud_details():
    # Gather all cloud details and return them, along with the fieldnames

    grains = {}

    aws = _get_aws_details()
    azure = _get_azure_details()
    gcp = _get_gcp_details()

    if aws['cloud_details']:
        grains.update(aws)
    if azure['cloud_details']:
        grains.update(azure)
    if gcp['cloud_details']:
        grains.update(gcp)

    return grains


def _get_aws_details():
    # Gather amazon information if present
    ret = {}
    aws = {}
    aws_extra = {}
    aws['cloud_instance_id'] = None
    aws['cloud_account_id'] = None
    aws['cloud_type'] = 'aws'

    try:
        res = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document',
                            timeout=3).json()
        aws['cloud_account_id'] = res.get('accountId', 'unknown')

        # AWS account id is always an integer number
        # So if it's an aws machine it must be a valid integer number
        # Else it will throw an Exception
        int(aws['cloud_account_id'])

        aws['cloud_instance_id'] = requests.get('http://169.254.169.254/latest/meta-data/instance-id',
                                                timeout=3).text
    except (requests.exceptions.RequestException, ValueError):
        # Not on an AWS box
        aws = None
    if aws:
        try:
            aws_extra['cloud_private_ip'] = res.get('privateIp')
            aws_extra['cloud_instance_type'] = res.get('instanceType')
            aws_extra['cloud_availability_zone'] = res.get('availabilityZone')
            aws_extra['cloud_ami_id'] = res.get('imageId')
            aws_extra['cloud_region'] = res.get('region')
            aws_extra['cloud_public_hostname'] = requests.get('http://169.254.169.254/latest/meta-data/public-hostname',
                                                              timeout=3).text
            aws_extra['cloud_public_ipv4'] = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4',
                                                          timeout=3).text
            aws_extra['cloud_private_hostname'] = requests.get('http://169.254.169.254/latest/meta-data/local-hostname',
                                                               timeout=3).text
        except (requests.exceptions.RequestException, ValueError):
            aws_extra = None

    ret['cloud_details'] = aws
    ret['cloud_details_extra'] = aws_extra
    return ret


def _get_azure_details():
    # Gather azure information if present
    ret = {}
    azure = {}
    azure_extra = {}
    azure['cloud_instance_id'] = None
    azure['cloud_account_id'] = None
    azure['cloud_type'] = 'azure'
    azureHeader = {'Metadata': 'true'}
    try:
        # Reminder: rev the api version for access to more details
        id = requests.get('http://169.254.169.254/metadata/instance/compute?api-version=2017-08-01',
                          headers=azureHeader, timeout=3).json()
        azure['cloud_instance_id'] = id['vmId']
        azure['cloud_account_id'] = id['subscriptionId']

    except (requests.exceptions.RequestException, ValueError):
        # Not on an Azure box
        azure = None

    if azure:
        try:
            azure_extra['cloud_resource_group_name'] = id['resourceGroupName']
            azure_extra['cloud_location'] = id['location']
            azure_extra['cloud_instance_name'] = id['name']
            azure_extra['cloud_image_offer'] = id['offer']
            azure_extra['cloud_os_type'] = id['osType']
            azure_extra['cloud_image_publisher'] = id['publisher']
            azure_extra['cloud_instance_tags'] = id['tags']
            azure_extra['cloud_image_version'] = id['version']
            azure_extra['cloud_instance_size'] = id['vmSize']
            interface = requests.get('http://169.254.169.254/metadata/instance/network/interface?api-version=2017-08-01',
                                     headers=azureHeader, timeout=3).json()
            for counter, value in enumerate(interface):
               grain_name_private_ipv4 = "cloud_interface_{0}_private_ipv4".format(counter)
               azure_extra[grain_name_private_ipv4] = value['ipv4']['ipAddress'][0]['privateIpAddress']
               grain_name_public_ipv4 = "cloud_interface_{0}_public_ipv4".format(counter)
               azure_extra[grain_name_public_ipv4] = value['ipv4']['ipAddress'][0]['publicIpAddress']
               grain_name_mac = "cloud_interface_{0}_mac_address".format(counter)
               azure_extra[grain_name_mac] = value['macAddress']

        except (requests.exceptions.RequestException, ValueError):
            azure_extra = None

    ret['cloud_details'] = azure
    ret['cloud_details_extra'] = azure_extra
    return ret

def _get_gcp_details():
    # Gather google compute platform information if present
    ret = {}
    gcp = {}
    gcp_extra = {}
    gcp['cloud_instance_id'] = None
    gcp['cloud_account_id'] = None
    gcp['cloud_type'] = 'gcp'
    gcp_header = {'Metadata-Flavor': 'Google'}
    try:
        gcp['cloud_instance_id'] = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/id',
                                                headers=gcp_header, timeout=3).text
        gcp['cloud_account_id'] = requests.get('http://metadata.google.internal/computeMetadata/v1/project/numeric-project-id',
                                               headers=gcp_header, timeout=3).text
    except (requests.exceptions.RequestException, ValueError):
        # Not on gcp box
        gcp = None
    if gcp:
        try:
            gcp_extra['cloud_project_id'] = requests.get('http://metadata.google.internal/computeMetadata/v1/project/project-id',
                                                         headers=gcp_header, timeout=3).text
            gcp_extra['cloud_instance_name'] = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/name',
                                                            headers=gcp_header, timeout=3).text
            gcp_extra['cloud_instance_hostname'] = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/hostname',
                                                                headers=gcp_header, timeout=3).text
            gcp_extra['cloud_instance_zone'] = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/zone',
                                                            headers=gcp_header, timeout=3).text
            gcp_extra['cloud_instance_image'] = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/image',
                                                             headers=gcp_header, timeout=3).text
            gcp_extra['cloud_instance_machine_type'] = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/machine-type',
                                                                     headers=gcp_header, timeout=3).text
            gcp_extra['cloud_instance_network_interfaces'] = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/?recursive=true',
                                                                          headers=gcp_header, timeout=3).json()
            gcp_extra['cloud_instance_tags'] = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/tags?recursive=true',
                                                            headers=gcp_header, timeout=3).json()
        except (requests.exceptions.RequestException, ValueError):
            gcp_extra = None

    ret['cloud_details'] = gcp
    ret['cloud_details_extra'] = gcp_extra
    return ret
