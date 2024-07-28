#!/usr/bin/env python

################################################################
# A build pipeline to automate python k8s project creation and deployment
# Avionix dependencies are remarked for simplicity (supporting latest python3 requires ditutils install + local build)
# This pipeline will generate a docker image and push it to local kind registry
# Helm chart generation is disabled (avionix)
################################################################

import sys
import os
import logging
import subprocess
import shutil
import argparse

# from avionix.chart import ChartBuilder, ChartInfo
# from avionix.kube.meta import ObjectMeta
# from avionix.kube.apps import Deployment, DeploymentSpec, PodTemplateSpec
# from avionix.kube.core import Container, ContainerPort, EnvVar, \
#     LabelSelector, PodSpec, Service, ServicePort, ServiceSpec, ServiceAccount, ConfigMap
# from avionix.kube.rbac_authorization import Role, RoleBinding, PolicyRule, RoleRef, Subject

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

ACTION_BUILD = 'build'
ACTION_CREATE = 'create'
ACTION_CLEAN = 'clean'
ALL_ACTIONS = [ACTION_BUILD, ACTION_CREATE, ACTION_CLEAN]
TEMPLATE_DIR = 'template'
HELM_DIR_FMT = 'helm-{}'

PORT = '5001'


def docker_cmd(*args):
    cmd = ['docker']
    cmd.extend(args)
    subprocess.check_output(cmd)


def docker_exec(msg, *args):
    logger.info("[MSG] {}".format(msg))
    logger.info("[ARGS] {}".format(args))
    try:
        docker_cmd(*args)
    except Exception as err:
        logger.warn(err)


def tree_cmd(dir_name):
    print('.')
    for file in os.listdir(dir_name):
        print('|- {}'.format(file))


def create_test_from_template(args):
    test_name = args.test
    shutil.copytree(TEMPLATE_DIR, test_name)
    print("==> created test dir: {}".format(test_name))
    tree_cmd(test_name)


def build_and_deploy_test(args):
    test_name = args.test
    docker_exec("build test container", 'build', test_name,
                '-t', '{}:latest'.format(test_name))
    docker_exec("tag test container", 'tag', '{}:latest'.format(
        test_name), 'localhost:{}/{}:latest'.format(PORT, test_name))
    docker_exec("push test container", 'push',
                'localhost:{}/{}:latest'.format(PORT, test_name))


# def helm_gen(args):
#     test_name = args.test
#     name = 'app-{}'.format(test_name)
#     labels = dict(app=test_name)
#     container = Container(
#         name="app",
#         image="localhost:5001/{}:latest".format(test_name),
#         image_pull_policy='Always',
#         env=[{"name": "POD_NAME","valueFrom": {"fieldRef": {"fieldPath": "metadata.name"}}}]
#     )
#     service_account = ServiceAccount(
#         metadata=ObjectMeta(name=name, labels=dict(app=name)),
#         automount_service_account_token=True
#     )
#     role = Role(
#         metadata=ObjectMeta(name=name, labels=dict(app=name)),
#         rules=[
#             PolicyRule(api_groups=['coordination.k8s.io'], resources=['*'], verbs=['*']),
#             PolicyRule(api_groups=[''], resources=['*'], verbs=['*']),
#         ]
#     )
#     role_binding = RoleBinding(
#         metadata=ObjectMeta(name=name, labels=dict(app=name)),
#         role_ref=RoleRef(
#             api_group='rbac.authorization.k8s.io',
#             kind='Role',
#             name=name
#         ),
#         subjects=[
#             Subject(kind='ServiceAccount', name=name),
#         ]
#
#     )
#     config_map = ConfigMap(
#         metadata=ObjectMeta(name=name, labels=labels),
#         data={}
#     )
#
#     deployment = Deployment(
#         metadata=ObjectMeta(name=name, labels=labels),
#         spec=DeploymentSpec(
#             replicas=3,
#             template=PodTemplateSpec(
#                 ObjectMeta(labels=labels),
#                 spec=PodSpec(
#                     containers=[container],
#                     automount_service_account_token=True,
#                     service_account=name,
#                     service_account_name=name,
#
#                 )
#             ),
#             selector=LabelSelector(match_labels=labels),
#         ),
#     )
#
#     builder = ChartBuilder(
#         ChartInfo(api_version="3.2.4", name=HELM_DIR_FMT.format(
#             test_name), version="0.1.0", app_version="v1"),
#         [deployment, role_binding, role, service_account, config_map]
#     )
#     builder.generate_chart()


# def clean(args):
#     test_name = args.test
#     if TEMPLATE_DIR == test_name:
#         print("{} dir is protected".format(TEMPLATE_DIR))
#         return
#     shutil.rmtree(test_name, ignore_errors=True)
#     shutil.rmtree(HELM_DIR_FMT.format(test_name), ignore_errors=True)


def main(args):
    if ACTION_BUILD == args.action:
        build_and_deploy_test(args)
        # helm_gen(args)

    # elif ACTION_CREATE == args.action:
    #     create_test_from_template(args)
    #
    # elif ACTION_CLEAN == args.action:
    #     clean(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='python to k8s builder')
    parser.add_argument('-t', dest="test", help='test-name', default='elected-api')
    parser.add_argument('-a', dest="action", choices=ALL_ACTIONS,
                        default=ACTION_BUILD, help='builder action')

    args = parser.parse_args()
    sys.exit(main(args))
