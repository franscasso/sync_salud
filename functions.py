import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()

def connect_to_supabase():
    """
    Connects to the Supabase PostgreSQL database using transaction pooler details
    and credentials stored in environment variables.
    """
    try:
        # Retrieve connection details from environment variables
        host = os.getenv("SUPABASE_DB_HOST")
        port = os.getenv("SUPABASE_DB_PORT")
        dbname = os.getenv("SUPABASE_DB_NAME")
        user = os.getenv("SUPABASE_DB_USER")
        password = os.getenv("SUPABASE_DB_PASSWORD")

        # Check if all required environment variables are set
        if not all([host, port, dbname, user, password]):
            print("Error: One or more Supabase environment variables are not set.")
            print("Please set SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME, SUPABASE_DB_USER, and SUPABASE_DB_PASSWORD.")
            return None

        # Establish the connection
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )
        print("Successfully connected to Supabase database.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to Supabase database: {e}")
        return None


def execute_query(query, params= None, conn=None, is_select=True):
    """
    Executes a SQL query and returns the results as a pandas DataFrame for SELECT queries,
    or executes DML operations (INSERT, UPDATE, DELETE) and returns success status.
    
    Args:
        query (str): The SQL query to execute
        conn (psycopg2.extensions.connection, optional): Database connection object.
            If None, a new connection will be established.
        is_select (bool, optional): Whether the query is a SELECT query (True) or 
            a DML operation like INSERT/UPDATE/DELETE (False). Default is True.
            
    Returns:
        pandas.DataFrame or bool: A DataFrame containing the query results for SELECT queries,
            or True for successful DML operations, False otherwise.
    """
    try:
        # Create a new connection if one wasn't provided
        close_conn = False
        if conn is None:
            conn = connect_to_supabase()
            close_conn = True
        
        # Create cursor and execute query
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if is_select:
            # Fetch all results for SELECT queries
            results = cursor.fetchall()
            
            # Get column names from cursor description
            colnames = [desc[0] for desc in cursor.description]
            
            # Create DataFrame
            df = pd.DataFrame(results, columns=colnames)
            result = df
        else:
            # For DML operations, commit changes and return success
            conn.commit()
            result = True
        
        # Close cursor and connection if we created it
        cursor.close()
        if close_conn:
            conn.close()
            
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        # Rollback any changes if an error occurred during DML operation
        if conn and not is_select:
            conn.rollback()
        return pd.DataFrame() if is_select else False

def add_user(dni, nombre_usuario, contraseña, rol):
    """
    Agrega un nuevo usuario a la tabla 'users'.
    """
    query = """
        INSERT INTO users (id, nombre_usuario, contraseña, rol)
        VALUES (%s, %s, %s, %s)
    """
    params = (dni, nombre_usuario, contraseña, rol)
    print(f"Ejecutando query: {query} con params: {params}")  # Depuración
    return execute_query(query, params=params, is_select=False)

connect_to_supabase()

def get_connection():
    return psycopg2.connect(
        host="aws-0-us-east-1.pooler.supabase.com",
        database="postgres",
        user="postgres.oubnxmdpdosmyrorjiqp",
        password="$EB6Y5rbR#z8_qh",
        port="5432"
    )
<<<<<<< Updated upstream


def autenticar_usuario(nombre_usuario, contraseña):
    """
    Verifica si el usuario existe y si la contraseña es correcta.

    Args:
        nombre_usuario (str): El nombre de usuario ingresado.
        contraseña (str): La contraseña ingresada.

    Returns:
        dict: {'success': bool, 'message': str}
    """
    query = "SELECT contraseña FROM users WHERE nombre_usuario = %s"
    params = (nombre_usuario,)
    resultado = execute_query(query, params=params, is_select=True)

    if resultado.empty:
        return {'success': False, 'message': 'El usuario no existe.'}
    
    contraseña_en_bd = resultado.iloc[0]['contraseña']
    
    if contraseña == contraseña_en_bd:
        return {'success': True, 'message': f'Bienvenido, {nombre_usuario}!'}
    else:
        return {'success': False, 'message': 'Contraseña incorrecta.'}

def buscar_rol(nombre_usuario, contraseña):
    """
    Devuelve el rol de un usuario si las credenciales son correctas.

    Args:
        nombre_usuario (str): Nombre de usuario ingresado.
        contraseña (str): Contraseña ingresada.

    Returns:
        dict: {'success': bool, 'rol': str or None, 'message': str}
    """
    query = "SELECT contraseña, rol FROM users WHERE nombre_usuario = %s"
    params = (nombre_usuario,)  
    resultado = execute_query(query, params=params, is_select=True)

    if resultado.empty:
        return {'success': False, 'rol': None, 'message': 'El usuario no existe.'}

    contraseña_en_bd = resultado.iloc[0]['contraseña']
    rol_en_bd = resultado.iloc[0]['rol']

    if contraseña == contraseña_en_bd:
        return {'success': True, 'rol': rol_en_bd, 'message': f"{rol_en_bd}"}
    
    

def verificar_medico_por_dni(dni):
    """
    Verifica si un médico existe por su DNI y devuelve el hospital al que pertenece.

    Args:
        dni (str or int): DNI del médico.

    Returns:
        dict: {'success': bool, 'id_hospital': int or None, 'message': str}
    """
    query = "SELECT id_hospital FROM medicos WHERE dni = %s"
    params = (dni,)
    resultado = execute_query(query, params=params, is_select=True)

    if resultado.empty:
        return {
            'success': False,
            'id_hospital': None,
            'message': 'No se encontró ningún médico con ese DNI.'
        }

    id_hospital = resultado.iloc[0]['id_hospital']
    return {
        'success': True,
        'id_hospital': id_hospital,
    }

def obtener_dni_por_usuario(nombre_usuario):
    """
    Devuelve el DNI (columna 'id') de un usuario a partir de su nombre de usuario.

    Args:
        nombre_usuario (str): Nombre de usuario registrado en la tabla 'users'.

    Returns:
        dict: {'success': bool, 'dni': str or None, 'message': str}
    """
    query = "SELECT id FROM users WHERE nombre_usuario = %s"
    params = (nombre_usuario,)
    resultado = execute_query(query, params=params, is_select=True)

    if resultado.empty:
        return {
            'success': False,
            'dni': None,
            'message': 'No se encontró ningún usuario con ese nombre.'
        }

    dni = resultado.iloc[0]['id']
    return {
        'success': True,
        'dni': f"{dni}",
        'message': f"El DNI del usuario '{nombre_usuario}' es {dni}."
    }
=======
>>>>>>> Stashed changes
