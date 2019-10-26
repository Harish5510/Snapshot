import boto3
import click

session = boto3.Session(profile_name='Mano')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

@click.group()
def instances():
    "Commands for instances"
@instances.command('list')
@click.option('--project', default=None,
    help="This will select all instance in Project Python")

def list_function(project):
    "List all Ec2 Instances"
    instances = filter_instances(project)

    for i in instances:
        tags = { t["Key"]: t['Value'] for t in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.state['Name'],
            i.placement['AvailabilityZone'],
            i.public_dns_name,
            tags.get('Project', '<no project>'))))
    return

@instances.command('stop')
@click.option('--project', default=None,
    help="This will select all instance in Project Python")

def stop_function(project):
    "stop all Ec2 Instances"
    instances = filter_instances(project)

    for i in instances:
        print("stopping {0}..".format(i.id))
        i.stop()
    return

@instances.command('start')
@click.option('--project', default=None,
    help="This will select all instance in Project Python")

def start_function(project):
    "start all Ec2 Instances"
    instances = filter_instances(project)

    for i in instances:
        print("start {0}..".format(i.id))
        i.start()
    return

instances()
