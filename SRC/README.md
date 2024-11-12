# Exam_108271

## How to Run

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/exam_108271.git
    cd exam_108271
    ```

2. **Create a virtuel Invirement**:
https://code.visualstudio.com/docs/python/environments

3. **Install the requrements**
Found in requirements.txt

4. **Run the application**:

    ```bash
    python3 -m flask run
    ```

    The application will start running at `http://127.0.0.1:5000`.

## Instructions for Testing

Use the following credentials to test the application:

### Existing Users

* **Username**: `oleander` 
  **Password**: `oleander`
* **Username**: `userone` 
  **Password**: `userone`

## List of All Functionality

### User Authentication

* **Login**: Users can log in using their username and password.
* **Register**: New users can register with a unique username and a password.
    * **Email**: New users use their email register a new account. This has basic check if what the user types is an email.
    * **Password**: Password must be minimum 3 characters, and there is a confirm password field that need to match the original field. 
    * **Fields**: All fields are required. 
* **Logout**: Logged-in users can log out.

### User Profile

* **View Profile**: Users can view their profile information.
* **Profile Picture**: Users' profile pictures are displayed on their profile pages, and on all tweets that the user makes.
* **Profile Bio**: Users bio are displayed on the profile pages
* **Edit Profile**: Users can update their profile information, including profile picture and bio.

### Error Handling

* **Password Validation**: If a user tries to register a password with less than 3 characters, an error is displayed.
* **Email Validation**: If a user tries to register a email without '@' or '.', an error is displayed. 
* **Profile Picture**: Users get assigned a default profile picture, when creating an account. 
* **Error**: Custom error page.
* **Error 404**: Custom page to tell the user if a page is not found. 

### Additional Features

* **Responsive Design**: The application is fully responsive and works well on most screen sizes.
* **Dark Mode**: The application uses a dark theme for better user experience.
* **Navbar**: A fully functional navigation bar with links to Home, Account, and other sections.

### Example Data

* **SQLite Database**: The project includes a pre-populated SQLite database with example data. This ensure a good testing experience.