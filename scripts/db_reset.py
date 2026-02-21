import argparse
import os
import sys
from sqlalchemy import create_engine

from database.base import Base
import entities.account_entity  # noqa: F401
import entities.loan_entity     # noqa: F401
import entities.offer_entity    # noqa: F401
import entities.plan_entity     # noqa: F401

def get_engine():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    return create_engine(db_url, pool_pre_ping=True)

def confirm(force: bool):
    if force:
        return
    print("DROPPING ALL TABLES. This deletes everything.")
    typed = input("Type DROP ALL to continue: ").strip()
    if typed != "DROP ALL":
        print("Aborted.")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["drop", "create", "reset"])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    engine = get_engine()

    if args.cmd in ("drop", "reset"):
        confirm(args.force)
        Base.metadata.drop_all(bind=engine)
        print("Dropped all tables")

    if args.cmd in ("create", "reset"):
        Base.metadata.create_all(bind=engine)
        print("Created all tables")

if __name__ == "__main__":
    main()