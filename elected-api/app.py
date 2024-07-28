import os
import uuid
import logging
from leader_election import LeaderElection
from kubernetes import client, config
from kubernetes.leaderelection.resourcelock.configmaplock import ConfigMapLock
from kubernetes.leaderelection import electionconfig

logger = logging.getLogger()
formatter = logging.Formatter(fmt="[%(asctime)s %(lineno)d]: %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
# logging.basicConfig(level=logging.INFO, format="<<< %(asctime)s %(lineno)d >>> %(message)s")

def load_kube_config():
    try:
        logger.info("attempt loading incluster k8s config")
        config.load_incluster_config()
    except:
        logger.info('[FAILED] loading incluster k8s config')
        try:
            logger.info("attempt loading k8s config")
            config.load_kube_config()
        except:
            logger.exception('[FAILED] loading k8s config')


# Authenticate using config file
load_kube_config()
# Parameters required from the user

# A unique identifier for this candidate
candidate_id = uuid.uuid4()

# Name of the lock object to be created
lock_name = "examplepython"

# Kubernetes namespace

lock_namespace = "default"


# The function that a user wants to run once a candidate is elected as a leader
def example_func():
    pod_name = os.environ.get('POD_NAME', 'NA')
    logger.info("\n<<<<<<<<<<<<<<<<<\n\t[LEADER] POD_NAME {} \n>>>>>>>>>>>>>>>>>>\n".format(pod_name))
    logger.info("\n<<<<<<<<<<<<<<<<<\n\t[LEADER] elected {} \n>>>>>>>>>>>>>>>>>>\n".format(candidate_id))


# A user can choose not to provide any callbacks for what to do when a candidate fails to lead - onStoppedLeading()
# In that case, a default callback function will be used

# Create config
try:
    pod_name = os.environ.get('POD_NAME', 'NA')
    logger.info("[POD-NAME] {}".format(pod_name))
    election_config = electionconfig.Config(ConfigMapLock(lock_name, lock_namespace, candidate_id), lease_duration=17,
                                            renew_deadline=15, retry_period=5, onstarted_leading=example_func,
                                            onstopped_leading=None)
    logger.info("[PASSED] election config set")
    LeaderElection(election_config).run()
    logger.info("[PASSED] election attempt")
except Exception as err:
    logger.exception(err)
# Enter leader election

# User can choose to do another round of election or simply exit
logger.info("[EXIT] leader election")


