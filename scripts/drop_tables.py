

from database.session import engine
from entities.entity_base import EntityBase

import entities.account_entity
import entities.federal_loan_entity
import entities.private_loan_entity
import entities.job_offer_entity
import entities.housing_profile_entity


def main() -> None:
    # python -m scripts.drop_tables
    tables = list(EntityBase.metadata.tables.keys())
    if not tables:
        print("No tables found. Nothing to drop.")
        return

    EntityBase.metadata.drop_all(engine)
    print("Dropped all tables")


if __name__ == "__main__":
    main()