import boto3
import click
import botocore

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
def cli():
    "This scripts manages our server maintanance"

@cli.group('volumes')
def volumes():
    "This manages volumes"
@volumes.command('list')
@click.option('--project', default=None,
    help="This will select all instance in Project Python")

def list_volumes(project):
    "List all volumes attached with Ec2 instances"
    instances = filter_instances(project)
    for i in list(instances):
        for v in i.volumes.all():
            print(', '.join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
                )))
    return

@cli.group('snapshots')
def snapshots():
    "This manages snapshots"
@snapshots.command('list')
@click.option('--project', default=None,
    help="This will select all snapshots in Project Python")

def list_snapshots(project):
    "List all snapshots associated with Ec2 instances"
    instances = filter_instances(project)
    for i in list(instances):
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    str(s.start_time.strftime("%c"))
                    )))
    return
@cli.group('instances')
def instances():
    "Commands for instances"

@instances.command('snapshot')
@click.option('--project', default=None,
    help="This will select all instance in Project Python")

def create_snapshots(project):
    "creates snapshots for instances"
    instances = filter_instances(project)
    for i in list(instances):
        print("stopping instance {}".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            print("Creating snopshot for volume{0}".format(v.id))
            v.create_snapshot(Description="Created by Pyton script")
            i.start()
            print("starting instance {}".format(i.id))
            i.wait_until_running()
    print("Job is done!!")
    return

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
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop instance {0} .".format(i.id) + str(e))

    return

@instances.command('start')
@click.option('--project', default=None,
    help="This will select all instance in Project Python")

def start_function(project):
    "start all Ec2 Instances"
    instances = filter_instances(project)

    for i in instances:
        print("start {0}..".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start instance {0} .".format(i.id) + str(e))
    return

if __name__ == '__main__':
    cli()
