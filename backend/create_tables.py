from sqlalchemy import inspect
from database import engine

def main():
    print("Connecting to the database to inspect tables...")
    try:
        # The 'inspector' object provides information about the database
        inspector = inspect(engine)
        
        # Get a list of table names
        table_names = inspector.get_table_names()
        
        if table_names:
            print("\nSuccess! Found the following tables:")
            for name in table_names:
                print(f"- {name}")
        else:
            print("\nConnection successful, but no tables were found in the database.")

    except Exception as e:
        print(f"\nAn error occurred while connecting or inspecting the database: {e}")

if __name__ == "__main__":
    main()