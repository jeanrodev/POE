
def authenticate_user(username, password):
    """Simple login function - VULNERABLE!"""
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    return result is not None
    
def process_user_input(user_data):
    """Process input without validation."""
    eval(user_data)  # DANGEROUS!
    return True
