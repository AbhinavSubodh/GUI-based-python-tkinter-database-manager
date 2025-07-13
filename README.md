# Organization Database Manager

A comprehensive desktop application built with Python Tkinter and MySQL to manage an organization's departments, projects, employees, and dependents. This tool is designed for HR teams, academic projects, or any organization needing a simple, local database management solution with a modern, user-friendly interface.

## Features

- **Department Management:** Add, update, delete, search, and import department records. View all department details in a sortable table.
- **Project Management:** Manage projects with department linkage, including CSV import and search functionality.
- **Employee Management:** Store employee details, including photos, assign to departments/projects, and import from CSV. View and update employee records easily.
- **Dependent Management:** Track dependents for each employee, including photo support and CSV import.
- **Photo Support:** Store and display photos for both employees and their dependents.
- **PDF Export:** Generate and download individual PDF reports for all employees, including their department, project, and dependents' information (with photos).
- **Modern UI:** Uses ttkbootstrap for a modern, responsive look and feel.
- **Automatic Database Setup:** The app creates the required MySQL database and tables on first run.

## Requirements

- Python 3.x
- MySQL Server
- Python packages:
  - ttkbootstrap
  - mysql-connector-python
  - Pillow
  - reportlab

## Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```
2. **Install dependencies:**
   ```bash
   pip install ttkbootstrap mysql-connector-python Pillow reportlab
   ```
3. **Set up MySQL:**
   - Ensure MySQL server is running.
   - The app will create the required database and tables on first run.
   - Default MySQL credentials used:
     - user: `project`
     - password: `internship`
     - host: `localhost`
   - You can change these in `organization.py` if needed.
4. **Run the application:**
   ```bash
   python organization.py
   ```

## Usage

- **Navigating Tabs:** Use the tabs to switch between Departments, Projects, Employees, and Dependents.
- **CRUD Operations:** Add, update, or delete records using the provided forms and buttons.
- **CSV Import:** On switching to a tab, you will be prompted to import data from a CSV file if desired.
- **Photo Upload:** For employees and dependents, use the "Select Photo" button to upload an image.
- **PDF Export:** In the Employee tab, use the "Download All Employees as Individual PDFs" button to export all employee records as PDFs.
- **Search:** Use the search bar in each tab to filter records by keyword.

## Notes

- All data is stored locally in your MySQL database.
- The application is intended for local/offline use.
- CSV import/export and PDF generation are available from within the app.
- You can customize MySQL credentials in the code if needed.

## License

This project is open-source and available under the MIT License.

--- 
