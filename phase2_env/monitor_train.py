import shlex
import subprocess
import click
import json
import sys
import logging
import os

logging.basicConfig(
    level='INFO',
    format='%(asctime)s [%(levelname)s]: %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__file__)


def train(train_data_path, team_config):
    team_name = team_config["team"]
    train_command = team_config["train"]
    persist_path = team_config["persist"]
    image_name = team_config["uuid"]
    logger.info("Team {} train start".format(team_name))

    command = "sudo nvidia-docker run --rm --ipc=host -v {persist}:{persist} -v {train_data}:{train_data} {image} {command} \"{persist}\" \"{train_data}\"".format(image=image_name, command=train_command, persist=persist_path, train_data=train_data_path)
    logger.info("Run command {}".format(command))
    client = subprocess.Popen(shlex.split(command))
    client.wait()

    logger.info("Team {} train end".format(team_name))


@click.command("Phase2 Train")
@click.option("--config-file-path", "-c", default="", help="Path to config JSON file, leave empty to use stdin")
@click.option("--train-data-path", "-t", help="Path to train data, which is supposed to be a csv file including at least three columns: KPI ID, timestamp, value")
def main(config_file_path, train_data_path):
    train_data_path = os.path.realpath(train_data_path)
    config_file_path = os.path.realpath(config_file_path)
    if config_file_path == "":
        config_file = sys.stdin
    else:
        config_file = open(config_file_path, "r")
    config_list = json.load(config_file)  # type: list
    list(map(lambda team_config: train(train_data_path, team_config), config_list))


if __name__ == '__main__':
    main()
