from python_freeipa import ClientMeta
import yaml


def get_client() -> ClientMeta:
    with open("freeipa_config.yml", "r") as stream:
        freeipa_config = yaml.safe_load(stream)
    hostname = freeipa_config["hostname"]
    username = freeipa_config["username"]
    password = freeipa_config["password"]
    client = ClientMeta(hostname, verify_ssl=False)
    client.login(username=username, password=password)
    return client

