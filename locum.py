from app import create_app

# Initialize the Flask app by calling the create_app function from the __init__.py file
app = create_app()

if __name__ == '__main__':
    # Run the app in debug mode for development
    app.run(debug=True)


