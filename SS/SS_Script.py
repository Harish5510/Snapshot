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

def volume_has_inprogress_SS(volume):
    snapshot = list(volume.snapshots.all())
    return snapshot and snapshot[0].state == "pending"

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
@click.option('--all','list_all', default=False, is_flag=True,
    help="This will select all snapshots if all is not given in the command")

def list_snapshots(project, list_all):
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
                if s.state == "completed" and not list_all : break
    return

@cli.group('instances')
def instances():
    "Commands for instances"

@instances.command('reboot')
@click.option('--project', default=None,
    help="This will reboot all instance in Project Python")
@click.option('--force', default=False, is_flag=True,
    help="This flag adds force option")

def reboot_instances(project, force):
    "reboot all ec2 server associated with project"
    instances = filter_instances(project)
    if project or force:
        for i in list(instances):
            print("rebooting instance {}.".format(i.id))
            i.reboot()
        return
    else:
        print("project or force flag is missing in the command. Hence exiting the opeartion")

@instances.command('snapshot')
@click.option('--project', default=None,
    help="This will select all instance in Project Python")
@click.option('--force', default=False, is_flag=True,
    help="This flag adds force option")

def create_snapshots(project, force):
    "creates snapshots for instances"
    if project or force:
        instances = filter_instances(project)
        for i in list(instances):
            print("stopping instance {}".format(i.id))
            i.stop()
            i.wait_until_stopped()
            for v in i.volumes.all():
                if volume_has_inprogress_SS(v):
                    print("skipping..snapshot is already in progress for volume {0}.".format(v.id))
                    continue

                print("Creating snopshot for volume{0}".format(v.id))
                v.create_snapshot(Description="Created by Pyton script")
                i.start()
                print("starting instance {}".format(i.id))
                i.wait_until_running()
        print("Job is done!!")
        return
    else:
        print("project or force flag is missing in the command. Hence exiting the opeartion")
        pass

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
@click.option('--force', default=False, is_flag=True,
    help="This flag adds force option")

def stop_function(project, force):
    "stop all Ec2 Instances"
    if project or force:
        instances = filter_instances(project)

        for i in instances:
            print("stopping {0}..".format(i.id))
            try:
                i.stop()
                print("stopping instance {}".format(i.id))
                i.wait_until_stopped()
            except botocore.exceptions.ClientError as e:
                print("Could not stop instance {0} .".format(i.id) + str(e))

        return
    else:
        print("project or force flag is missing in the command. Hence exiting the opeartion")
        pass

@instances.command('start')
@click.option('--project', default=None,
    help="This will select all instance in Project Python")
@click.option('--force', default=False, is_flag=True,
    help="This flag adds force option")
def start_function(project, force):
    "start all Ec2 Instances"
    if project or force:
        instances = filter_instances(project)

        for i in instances:
            print("start {0}..".format(i.id))
            try:
                i.start()
                print("starting instance {}".format(i.id))
                i.wait_until_running()
            except botocore.exceptions.ClientError as e:
                print("Could not start instance {0} .".format(i.id) + str(e))
        return
    else:
        print("project or force flag is missing in the command. Hence exiting the opeartion")
        pass

if __name__ == '__main__':
    cli()
