import boto3
import click

session = boto3.Session(profile_name='Mano')
ec2 = session.resource('ec2')

def filter_instances(prjct_name):
    instances = []
    if prjct_name:
        filters = [{'Name':'tag:Project', 'Values':[prjct_name]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

@click.group()

def instances():
    "Commands for actions"

@instances.command('list')
@click.option('--prjct_name', default=None,
    help="This will select all instance for project")

def list_instances(prjct_name):
    "Listing ec2 instances"
    instances = filter_instances(prjct_name)
    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags}
        print(', '.join((
            i.id,
            i.state['Name'],
            i.placement['AvailabilityZone'],
            i.public_dns_name,
            tags.get('Project', '<no vlaue>'))))
    return

@instances.command('stop')
@click.option('--prjct_name', default=None,
    help="This will select all instance for project")

def stop_instances(prjct_name):
    "shutdown ec2 instances"
    instances = filter_instances(prjct_name)
    for i in instances:
        print("stopping {0}..".format(i.id))
        i.stop()

@instances.command('start')
@click.option('--prjct_name', default=None,
    help="This will select all instance for project")

def start_instances(prjct_name):
    "start ec2 instances"
    instances = filter_instances(prjct_name)
    for i in instances:
        print("starting {0}..".format(i.id))
        i.start()

if __name__ == '__main__':
    instances()
