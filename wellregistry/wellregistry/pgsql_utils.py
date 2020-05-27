"""
A collection of helper methods to construct postgres DDL SQL.

"""


def create_login_role(username, password):
    """Helper method to construct SQL: create role."""
    # "create role if not exists" is not valid syntax
    return f"DROP ROLE IF EXISTS {username}; CREATE ROLE {username} WITH CREATEROLE LOGIN PASSWORD '{password}';"


def drop_role(role):
    """Helper method to construct SQL: drop role."""
    return f"DROP ROLE IF EXISTS {role};"


def grant_role(role, target):
    """Helper method to construct SQL: grant privilege."""
    return f"GRANT {role} to {target};"


def revoke_role(role, target):
    """Helper method to construct SQL: revoke privilege."""
    return f"REVOKE {role} from {target};"


def grant_default(schema, defaults, target):
    """Helper method to construct SQL to grant default privileges."""
    if defaults == 'CRUD':
        defaults = "INSERT, SELECT, UPDATE, DELETE"

    return f"""
        ALTER DEFAULT PRIVILEGES 
        IN SCHEMA {schema} 
        GRANT {defaults} 
        ON TABLES TO {target};
    """


def revoke_default(schema, defaults, target):
    """Helper method to construct SQL to revoke default privileges."""
    if defaults == 'CRUD':
        defaults = "INSERT, SELECT, UPDATE, DELETE"

    return f"""
        ALTER DEFAULT PRIVILEGES 
        IN SCHEMA {schema} 
        REVOKE {defaults} 
        ON TABLES FROM {target}
    """
