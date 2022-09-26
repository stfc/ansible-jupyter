from python_freeipa import ClientMeta
import yaml
import os


def get_client() -> ClientMeta:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir,'freeipa_config.yml')
    with open(config_path, "r") as stream:
        freeipa_config = yaml.safe_load(stream)
    hostname = freeipa_config["hostname"]
    username = freeipa_config["username"]
    password = freeipa_config["password"]
    client = ClientMeta(hostname, verify_ssl=False)
    client.login(username=username, password=password)
    return client
