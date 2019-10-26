import boto3
import click

session = boto3.Session(profile_name='Mano')
ec2 = session.resource('ec2')

@click.command()
def list_function():
    "List all Ec2 Instances"
    for i in ec2.instances.all():
        print(', '.join((
        i.id,
        i.instance_type,
        i.state['Name'] ,
        i.placement['AvailabilityZone'],
        i.public_dns_name)))
    return

if __name__ == '__main__':
    list_function()
