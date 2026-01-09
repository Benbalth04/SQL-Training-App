## Build Overview
This application is compiled using a Python library called PyInstaller, which will bundle all Python libraries, code and assets (e.g. images) into a single executable file. 

To compile the code into the executable, you need to run the following command in the terminal. When doing so, ensure that your current directory is in the root folder of this application (e.g. the folder where the app.py file is located.). 

**Ensure you have the PyInstaller Python package installed by running the install_requirements.py file in the /tools folder.**

```
python -m PyInstaller --name "SQL Training App" --add-data "static;static" --add-data "lessons;lessons" --onefile --noconsole --icon=static\assets\icon.ico app.py
```

### After Running The Build Command
- The executable will be placed in the /dist folder
- It can be safely given to users to run on their device

### Key Implementation Notes 
- The application can run as a completely standalone process. 
    - This is achieved by having a new SQLite Database run on the user's local machine everytime they run the application
- When the .exe file is run, the database and Python Flask webserver will both startup
    - Once complete, a tab will be opened in the user's default browser with the app's URL (http://127.0.0.1:8000/)
    - It is important to note that **closing the browser tab WILL NOT end the Python application**, this process can only be killed via the Windows Task Manager, or when the user Shuts Down their device. 
    - To prevent too many processes starting and overwhelming the user's computer, the Flask app will check if the app is already running before initialising. If there is another instance running, the webbrowswer will just be opened instead of creating an entire new process of the application. 

        ```python 
        if __name__ == "__main__":
            if check_if_running():
                print("App already running. Skipping initialization...")
                webbrowser.open_new(APP_URL)
            else:
                print("No existing instance found. Running full startup...")
                DB_PATH = "file:shared_db?mode=memory&cache=shared"
                DB_INIT_CONN = sqlite3.connect(DB_PATH, uri=True, check_same_thread=False)

                detect_and_validate_lessons()
                run_init_sql()
                load_database_tables()
                print("Loaded tables:", DATABASE_TABLES)
                print(f"Loaded {len(LESSON_LIST)} lessons")
                print(f"Loaded {len(TASKS_LIST)} tasks")
                webbrowser.open_new(APP_URL)
                app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)
        ```