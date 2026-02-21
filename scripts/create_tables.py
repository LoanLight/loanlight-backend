"""
Create all database tables (hackathon-friendly).
Run:
  python -m scripts.create_tables
"""

from database.session import engine
from entities.entity_base import EntityBase

# Import ALL entity modules so metadata is registered
import entities.account_entity
import entities.federal_loan_entity
import entities.private_loan_entity
import entities.job_offer_entity
import entities.housing_profile_entity


def main() -> None:
    EntityBase.metadata.create_all(engine)
    print("Created all tables")


if __name__ == "__main__":
    main()