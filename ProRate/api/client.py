import requests
import sys
import json
from prettytable import PrettyTable
from tabulate import tabulate

BASE_URL = "sc222aa.pythonanywhere.com"
session = requests.Session()

def init_csrf():
    session.get(BASE_URL)

#this function will send HTTP requests to an API endpoint and print the JSON response in a readable format.
def make_request(method, endpoint, data=None):
    url = BASE_URL + endpoint

    headers = {}

    if 'csrftoken' in session.cookies:
        headers['X-CSRFToken'] = session.cookies['csrftoken']

    if method == "POST":
        response = session.post(url, json=data, headers=headers)
    elif method == "GET":
        response = session.get(url)
    elif method == "DELETE":
        response = session.delete(url)
    else:
        response = session.put(url,json=data)
    if endpoint == "api/ratings/" and method == "POST":
        if response.status_code in [200, 201]:
            print("Your rating has been submitted.")
        else:
            # Print friendly error messages if fields are missing or incorrect.
            try:
                error_data = response.json()
                for field, messages in error_data.items():
                    print(f"Error in '{field}': {', '.join(messages)}")
            except json.JSONDecodeError:
                print("An error occurred, and the response could not be parsed.")
    else:
        try:
            print(json.dumps(response.json(), indent=4))
        except json.JSONDecodeError:
            print("Response is not valid JSON, Raw response:")
            print(response.text)

def register():
    username = input("Username: ")
    email = input("Email: ")
    password = input("Password: ")
    make_request("POST", "api/register/", {"username": username, "email": email, "password": password})

def login():
    init_csrf()
    username = input("Username: ")
    password = input("Password: ")
    make_request("POST", "api/login/", {"username": username, "password": password})
    

def logout():
    make_request("POST", "api/logout/")

def list_modules():
    url = BASE_URL + "api/modules/"
    response = requests.get(url)
    try:
        modules = response.json()
        table = PrettyTable()
        table.field_names = ["Code", "Name", "Semester", "Year", "Professors"]
        for module in modules:
            professors = ", ".join(
                    f'{prof["name"]} ({prof["identifier"]})'
                    for prof in module.get("professors", [])
                    )
            table.add_row([
                module.get("code"),
                module.get("name"),
                module.get("semester"),
                module.get("year"),
                professors if professors else "None"
                ])
        print(table)
    except json.JSONDecodeError:
        print("Response is not valid JSON. this is the Raw Response")
        print(response.text)

def list_professors():
    url = BASE_URL + "api/professors/"
    response = requests.get(url)

    try:
        professors = response.json()
        table = PrettyTable()
        table.field_names = ["Identifier", "Name", "Avg Rating"]

        for professor in professors:
            table.add_row([
                professor.get("identifier"),
                professor.get("name"),
                professor.get("avg_rating")
            ])
        print(table)
    except json.JSONDecodeError:
        print("Response is not valid JSON. Raw response:")
        print(response.text)

def average_rating():
    professor_id = input("Enter professor ID: ")
    module_code = input("Enter module code: ")  # This line was missing.
    url = BASE_URL + f"api/ratings/average/?professor={professor_id}&module={module_code}"
    response = session.get(url)
    try:
        data = response.json()
        if response.status_code == 200:
            print(f"Professor {professor_id} has an average rating of: {data['average']}")
        else:
            print("Error:", data)
    except json.JSONDecodeError:
        print("Response is not valid JSON, Raw response:")
        print(response.text)


def rate_professor():
    professor_id = input("Professor ID: ")
    module_code = input("Module Code: ")
    year = input("Year: ")
    semester = input("Semester: ")
    rating = int(input("Rating (1-5): "))

    make_request("POST", "api/ratings/", {
        "professor": professor_id,
        "module": module_code,
        "year": year,
        "semester": semester,
        "rating": rating
        })

def print_help():
    print("Available commands:")
    print("  register - Register a new user")
    print("  login - Log in")
    print("  logout - Log out")
    print("  view - List of all professors and their average rating")
    print("  list - List all modules")
    print("  Average - View average rating of professor in certain module")
    print("  rate - Rate a professor")
    print("  help - Show this message")

commands = {
    "register": register,
    "login": login,
    "logout": logout,
    "view": list_professors,
    "list": list_modules,
    "average": average_rating,
    "rate": rate_professor,
    "help": print_help
}

def shell():
    print("Welcome! Enter a command, if you need help type 'help' and 'exit' to quit")

    while True:
            cmd = input("> ").strip().lower()
            if cmd == "exit":
                break
            elif cmd in commands:
                commands[cmd]()
            else:
                print("Unknown command. Type 'help' for available commands.")
    
if __name__ == "__main__":
    # If no command-line argument is provided, run interactive mode.
    if len(sys.argv) == 1:
        shell()
    else:
        command = sys.argv[1].lower()
        if command in commands:
            commands[command]()
        else:
            print("Invalid command, please use 'help' to see available commands.")


