from src.database.db_manager import (
    setup_database,
    validate_database,
)


def main():

    print("Initializing PROJECT RU'YA database...")

    setup_database()

    validate_database()

    print("\nPROJECT RU'YA database setup completed!")


if __name__ == "__main__":
    main()