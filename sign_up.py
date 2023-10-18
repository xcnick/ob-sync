import argparse
from obsync.db.vault_schema import new_user


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, required=True)
    parser.add_argument("-e", "--email", type=str, required=True)
    parser.add_argument("-p", "--password", type=str, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    user_model = new_user(
        name=args.name, email=args.email, password=args.password
    )
    if user_model is not None:
        print("User created successfully.")
    else:
        print("Sign up user failed.")
