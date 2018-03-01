import click
import os
import uuid
import json
import logging
import sys

logging.basicConfig(
    level='INFO',
    format='%(asctime)s [%(levelname)s]: %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__file__)


@click.command("Build Env")
@click.option("--base-dir", "-b", help="The dir that contains all teams' docker context. All sub-dir(not recursive) will be considered as a docker context", default=os.getcwd())
@click.option("--output", "-o", default=None)
def main(base_dir, output):
    config_list = []
    for context in os.listdir(base_dir):
        context = os.path.realpath(os.path.join(base_dir, context))
        if not os.path.isdir(context):
            continue
        logger.info("Parse context {}".format(context))
        # read config file and allocate persist path
        config_path = os.path.join(context, "config.json")
        if not os.path.isfile(config_path):
            logger.error("Can't find config.json. Skip {}".format(context))
            continue
        with open(config_path, "rb+") as f:
            config = json.load(f)
        config["uuid"] = str(uuid.uuid3(uuid.NAMESPACE_URL, config["team"]))  # generate uuid based on team name
        config["persist"] = "/srv/iops_phase2/{}".format(config["uuid"])
        os.makedirs(config["persist"], exist_ok=True)
        config_list.append(config)
        logger.info(config)
        # build docker image
        os.system("sudo nvidia-docker build {context} -t {tag}".format(context=context, tag=config["uuid"]))
        logger.info("Build Docker image successfully")
    if output is None:
        output = sys.stdout
    else:
        output = open(output, "w+")
    print(json.dumps(config_list), file=output)
    output.close()


if __name__ == '__main__':
    main()
