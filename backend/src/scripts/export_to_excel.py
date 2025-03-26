import mysql.connector
import pandas as pd
from core.config import settings

def export_tables_to_excel():
    """Export all tables from MySQL database to Excel file."""
    try:
        # Database connection configuration
        config = {
            'user': settings.db_user,
            'password': settings.db_password,
            'host': settings.db_host,
            'database': settings.db_database
        }

        # Connect to the database
        connection = mysql.connector.connect(**config)
        print("Successfully connected to MySQL database")

        # List of tables to export
        tables = ['inventory', 'orders', 'users', 'conversations']

        # Dictionary to store DataFrames
        dataframes = {}

        # Get data from each table
        for table in tables:
            query = f"SELECT * FROM {table}"
            try:
                dataframes[table] = pd.read_sql(query, connection)
                print(f"Successfully retrieved data from {table}")
            except Exception as e:
                print(f"Error retrieving data from {table}: {e}")

        # Save to Excel file with multiple sheets
        output_file = 'database_export.xlsx'
        with pd.ExcelWriter(output_file) as writer:
            for table, df in dataframes.items():
                # Convert datetime columns to string to avoid Excel date issues
                for column in df.select_dtypes(include=['datetime64[ns]']).columns:
                    df[column] = df[column].astype(str)
                
                df.to_excel(writer, sheet_name=table, index=False)
                print(f"Successfully wrote {table} to Excel")

        print(f"Excel file '{output_file}' created successfully")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    export_tables_to_excel()