from python_freeipa import ClientMeta
import argparse
from get_client import get_client


def delete_single_user(client: ClientMeta, user: str) -> None:
    user = client.user_del(a_uid=user)
    print(user["result"]["uid"], user["result"]["randompassword"])


def delete_users(basename: str, start_index: int, end_index: int) -> None:
    client = get_client()
    users = []
    for i in range(start_index, end_index + 1):
        users.append(f"{basename}-{i}")
    user = client.user_del(a_uid=users)
    print(user["value"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basename", help="User basename", type=str)
    parser.add_argument("--first_index", help="First index for usernames", type=int)
    parser.add_argument("--last_index", help="First index for usernames", type=int)
    args = parser.parse_args()

    basename = args.basename
    first_index = args.first_index
    last_index = args.last_index

    delete_users(basename, first_index, last_index)


if __name__ == "__main__":
    main()

