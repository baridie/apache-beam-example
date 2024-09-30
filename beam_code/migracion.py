import os
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import mysql.connector
import psycopg2
from argparse import ArgumentParser
import time


# Configuración de las conexiones a las bases de datos
mysql_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    }

postgres_config = {
    'host': os.getenv('POSTGRES_HOST'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DATABASE')
    }


# Agregar argumentos para lectura de tablas
parser = ArgumentParser()
parser.add_argument('--mysql-table', help='Nombre de la tabla en MySQL', required=True)
parser.add_argument('--postgres-table', help='Nombre de la tabla en PostgreSQL', required=False)
args = parser.parse_args()

print(f'Argumentos: {args}')
print(f'Configuración MySQL: {mysql_config}')
print(f'Configuración PostgreSQL: {postgres_config}')


# Configuración de las tablas
mysql_table = args.mysql_table
postgres_table = args.postgres_table if args.postgres_table else mysql_table


# Función para leer la estructura de la tabla desde MySQL
def get_table_structure():
    """
    Connects to a MySQL database and retrieves the structure of a specified table.
    This function establishes a connection to a MySQL database using the provided
    configuration, executes a DESCRIBE query on the specified table, and returns
    the structure of the table.
    Returns:
        list: A list of tuples where each tuple contains information about a column
              in the table, such as field name, type, nullability, key, default value,
              and extra information.
    Raises:
        mysql.connector.Error: If there is an error connecting to the database or
                               executing the query.
    """
    print('Obteniendo estructura de la tabla en MySQL')
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    
    # Obtén la estructura de la tabla
    cursor.execute(f"DESCRIBE {mysql_table}") 
    columns = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return columns

# Función para crear la tabla en PostgreSQL si no existe
def create_table_in_postgres(table_structure):
    """
    Creates a table in PostgreSQL based on the provided table structure.
    Args:
        table_structure (list of tuples): A list where each tuple contains the column name and its MySQL data type.
                                           Example: [('id', 'int'), ('name', 'varchar(255)'), ('created_at', 'datetime')]
    Returns:
        None
    Raises:
        psycopg2.DatabaseError: If there is an error while connecting to the database or executing the SQL query.
    Example:
        table_structure = [
            ('id', 'int'),
            ('name', 'varchar(255)'),
            ('created_at', 'datetime')
        ]
        create_table_in_postgres(table_structure)
    """
    print('Creando tabla en PostgreSQL')
    conn = psycopg2.connect(**postgres_config)
    cursor = conn.cursor()
    
    # Crea la sentencia SQL para crear la tabla
    create_table_query = f"CREATE TABLE IF NOT EXISTS {postgres_table} ("
    columns_definitions = []
    
    for column in table_structure:
        column_name = column[0]
        mysql_type = column[1]
        
        # Mapea tipos de datos de MySQL a PostgreSQL
        if 'int' in mysql_type:
            postgres_type = 'INTEGER'
        elif 'varchar' in mysql_type or 'text' in mysql_type:
            postgres_type = 'TEXT'
        elif 'datetime' in mysql_type:
            postgres_type = 'TIMESTAMP'
        elif 'decimal' in mysql_type:
            postgres_type = 'DECIMAL'
        else:
            postgres_type = 'TEXT'  # Ajusta según lo que necesites
        
        columns_definitions.append(f"{column_name} {postgres_type}")
    
    create_table_query += ", ".join(columns_definitions) + ");"
    
    # Ejecuta la consulta para crear la tabla
    cursor.execute(create_table_query)
    conn.commit()
    
    cursor.close()
    conn.close()

# Función para leer datos de MySQL
def read_from_mysql():
    """
    Connects to a MySQL database using the provided configuration, executes a query to select all rows from a specified table,
    and yields each row one by one.
    Yields:
        tuple: A tuple representing a row from the specified table in the MySQL database.
    Raises:
        mysql.connector.Error: If there is an error connecting to the MySQL database or executing the query.
    """
    print('Leyendo datos de MySQL')
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {mysql_table}")
    for row in cursor.fetchall():
        yield row
    
    cursor.close()
    conn.close()

# Función para escribir datos en PostgreSQL
def write_to_postgres(row):
    """
    Writes a row of data to a PostgreSQL table.
    This function connects to a PostgreSQL database using the configuration
    specified in `postgres_config`, and inserts the provided row into the
    table specified by `postgres_table`.
    Args:
        row (tuple): A tuple containing the data to be inserted into the PostgreSQL table.
    Raises:
        psycopg2.DatabaseError: If there is an error while connecting to the database
                                or executing the insert query.
    Example:
        row = (1, 'John Doe', 'johndoe@example.com')
        write_to_postgres(row)
    """

    print('Escribiendo datos en PostgreSQL')
    conn = psycopg2.connect(**postgres_config)
    cursor = conn.cursor()
    
    insert_query = f'''
    INSERT INTO {postgres_table} VALUES ({', '.join(['%s' for _ in range(len(row))])})
    ''' 
    
    cursor.execute(insert_query, row)
    conn.commit()
    
    cursor.close()
    conn.close()

def run():
    print('Iniciando pipeline')
    # Configuración de opciones del pipeline
    pipeline_options = PipelineOptions()

    # Obtén la estructura de la tabla de MySQL
    table_structure = get_table_structure()
    
    # Crea la tabla en PostgreSQL si no existe
    create_table_in_postgres(table_structure)

    # Pipeline de Apache Beam
    with beam.Pipeline(options=pipeline_options) as p:
        # Lee de MySQL
        rows = (p | 'ReadFromMySQL' >> beam.Create(read_from_mysql()))
        
        # Escribe en PostgreSQL
        rows | 'WriteToPostgres' >> beam.Map(write_to_postgres)
    
    print('Pipeline finalizado')

if __name__ == '__main__':
    # Dormir por 10 segundos para dar tiempo a que MySQL y PostgreSQL se inicien
    print('Esperando 10 segundos...')
    time.sleep(10)

    run()
