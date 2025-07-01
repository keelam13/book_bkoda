# BKODA Seat Reservation

Live Version: [BKODA Seat Reservation](https://book-bkoda-6d62942dbe76.herokuapp.com/)


Repository: [GitHub Repo](https://github.com/keelam13/book_bkoda)

The app is developed by [Keevin Aroco](https://github.com/keelam13).

![book BKODA](documentation/design/book_bkoda_logo.png)

## About

[book BKODA](https://github.com/keelam13/book_bkoda) book BKODA is a web application built with Django that allows users to easily reserve seats for travels from Kabayan, Benguet to Baguio City and vice versa. It provides a user-friendly interface for trip search, seat reservation and booking management.

## User Experience Design

### Strategy

Developed for the BKODA in the Municipality of Kabayan Benguet in the Philippines. The President of the association wanted an app where clients could easily reserve seats for the trips from Kabayan, Benguet to Baguio City and back. In this locality, the clients usually pay in cash and most of them don't have debit/credit cards. In this project, I enable users to pay with card (debit/credit) if they have, or else they may also opt to pay cash or money wallet (e.g. GCash). GCash is specifically included as an option since it is already being used by many in the area. If they also want to pay with cash, they may pay in selected payment centers or directly to the terminal. However, for offline payment, e.i cash and GCash, they are given up to 24 hours to pay for the booking to be confirmed, and a cutoff time will be observed. All of which are outlined in the Booking policy.

The application focuses on simplicity and efficiency, ensuring that users can quickly and easily reserve their desired number of seats. The design prioritizes clear navigation and a straightforward reservation process to minimize user frustration.

### Target Audience

This application is designed for:

* **Passengers:** Individuals seeking to reserve seats for transportation to and from the said areas.
* **Transportation Companies/Administrators:** To manage routes, seat availability, and reservation/bookings.

### User Stories

User Story ID AS A/AN I WANT TO BE ABLE TO... SO THAT I CAN...

#### **Searching and Viewing**
1 Passenger Search for trips Select one to book
2 Passenger View individual trip details Identify the route, date and time of departure and arrival, available seats, and the price

#### **Registration and User Accounts**
3 Site User Easily register for an account Have a personal account and be able to view my profile
4. Site User Easily register with my social account Register with my Facebook or Gmail accounts
4 Site User Easily login or logout Access my personal account information
5 Site User Easily recover my password in case I forget it Recover access to my account
6 Site User Receive an email confirmation after registering Verify that my account registration was successful
7 Site User Have a personalized user profile View my personal trip history and booking confirmations, and save my payment information

#### **Booking**
8 Passenger Easily select the trip that I want to book Ensure I don't accidentally select the wrong trip
9 Passenger Add the passengers Easily make changes before booking
10 Passenger Easily enter my payment information Check out quickly and with no hassles
11 Passenger Feel my personal and payment information is safe and secure Confidently provide the needed information to make a purchase
12 Passenger View an booking confirmation Verify that I haven't made any mistakes
13 Passenger Receive an email confirmation after payment Keep the confirmation of what I've paid for.
14 Passenger Easily manage my booking Change the date and/or time of my travel when I have to

#### **Admin and Transport Management**
15 Manager Add a trip Add new trips to the list
16 Manager Easily see bookings Easily plan for the next trips

---

## Technologies used

- ### Languages:
    
    + [Python 3.11.2](https://www.python.org/downloads/release/python-3112/): the primary language used to develop the server-side of the website.
    + [JS](https://www.javascript.com/): the primary language used to develop interactive components of the website.
    + [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML): the markup language used to create the website.
    + [CSS](https://developer.mozilla.org/en-US/docs/Web/css): the styling language used to style the website.

- ### Frameworks and libraries:

    + [Django](https://www.djangoproject.com/): python framework used to create all the logic.
    + [Django-allauth](https://django-allauth.readthedocs.io/en/latest/): the authentication library used to create the user 
    + [Django-crispy-forms](https://django-cryptography.readthedocs.io/en/latest/): was used to control the rendering behavior of Django forms.
    + [Bootstrap](https://getbootstrap.com/):was used to style the page

- ### Databases:

    + [SQLite](https://www.sqlite.org/): was used as a development database.
    + [PostgreSQL](https://www.postgresql.org/): the database used to store all the data.

- ### Other tools:

    + [Git](https://git-scm.com/): the version control system used to manage the code.
    + [Pip3](https://pypi.org/project/pip/): the package manager used to install the dependencies.
    + [Gunicorn](https://gunicorn.org/): the webserver used to run the website.
    + [Spycopg2](https://www.python.org/dev/peps/pep-0249/): the database driver used to connect to the database.
   accounts.
    + [GitHub](https://github.com/): used to host the website's source code.
    + [Heroku](https://heroku.com): used to host the website
    + [VSCode](https://code.visualstudio.com/): the IDE used to develop the website.
    + [Chrome DevTools](https://developer.chrome.com/docs/devtools/open/): was used to debug the website.
    + [Font Awesome](https://fontawesome.com/): was used to create the icons used in the website.
    + [Coolors](https://coolors.co/202a3c-1c2431-181f2a-0b1523-65e2d9-925cef-6b28e0-ffffff-eeeeee) was used to make a color palette for the website.
    * [Figma](https://figma.com/): was used to create the wireframes and the flowchart.
    + [W3C Validator](https://validator.w3.org/): was used to validate HTML5 code for the website.
    + [W3C CSS validator](https://jigsaw.w3.org/css-validator/): was used to validate CSS code for the website.
    + [JShint](https://jshint.com/): was used to validate JS code for the website.
    + [PEP8](https://pep8.org/): was used to validate Python code for the website.

---

## FEATURES

Please refer to the [FEATURES.md](FEATURES.md) file for all features-related documentation.

---

## Design

The design of the application is based on the Material Design principles.

The application's design prioritizes usability and clarity. A clean and modern interface ensures a smooth booking experience for passengers.


### Color Scheme

The color scheme of the application is based on the bold colors:

  ![Color Scheme](documentation/design/color_palette.png)

## Color Scheme

The Coder opted to use simple colors using the colors from the Bootstrap Color Class, e.i. Primary (Blue), Danger (Red) and Success (Green).
* **Red:** Used for "Cancel" and "Delete" buttons, indicating actions that require caution.
* **Blue:** Used for the "Update" button, aligning with the overall theme and suggesting a positive action.
* **Green:** Used for the "Previous Day," "Next Day," and "Reserve" buttons. The choice of green is intended to signal positive actions and encourage user engagement. Green is often associated with "go" signals and safe operations, making it suitable for these interactive elements. However, careful consideration was given to ensure sufficient contrast against the light blue background to maintain readability and accessibility.
* **Yellow:** Used for buttons and messages, to warn the user of pending or for bookings requiring actions.

The application primarily utilizes a light blue (#69DDFF) as the table background, creating a calm and trustworthy interface. 

The application employs black and white texts for primary contents depending on the color contrast between text and background to ensure high readability and clear visibility.

### Typography

The application employs Bootstrap's default font stack to ensure cross-platform compatibility and optimal performance. This stack is designed to utilize fonts that are natively available on the user's operating system, prioritizing `Helvetica Neue`, `Helvetica`, and `Arial`. A generic `sans-serif` font is used as a fallback to guarantee that text is displayed correctly even if the preferred fonts are not present. This strategy minimizes load times and ensures a consistent visual experience for users across different devices and operating systems.

Google font `Lilith One` was also used for the logo to it to stand out a bit from the rest of the texts.

![Google Font](documentation/design/google_font.png)

### Imagery

The background image is a shot from the boundary of Kabayan, Benguet's, a scene that resonates with the Kabayan people.

  ![Background](documentation/design/welcome_kabayan.webp)

* Warm, earthy tones: such as soft browns, beiges, and muted oranges, to evoke a sense of home and comfort.
* Accents of vibrant colors: like the blues of the Philippine flag or the greens of tropical landscapes, to add visual interest and cultural relevance.
* A neutral background: to allow the image to stand out and create a welcoming atmosphere.
* Soft lighting effects: to create a sense of warmth and familiarity.


### Wireframes

Since the project is a continued development from the previous BKODA Seat Reservation app, the wireframes and flowchart are the same with some changes and improvements.

## Desktop and Tablets

* Home Display

![Desktop Home](documentation/wireframes/desktop_home.png)

* Sign Up Form Display

![Desktop Sign Up Form](documentation/wireframes/desktop_signup.png)

* Logged in Display

![Desktop Logged in](documentation/wireframes/desktop_logged_in.png)

* Trip List Display

![Desktop Trip List](documentation/wireframes/desktop_triplist.png)

* Reservation Formm Display

![Desktop Reservation Form](documentation/wireframes/desktop_reservation_form.png)

* Reservation List Display

![Desktop Reservation List](documentation/wireframes/desktop_reservation_list.png)

* Reservation Cancelation Display

![Desktop Reservation Cancelation](documentation/wireframes/desktop_cancel_confirmation.png)

* Log Out Confirmation Display

![Desktop Logout Confirmation](documentation/wireframes/desktop_logout_confirmation.png)

## Mobile Devices

* Home Display

![Mobile Home](documentation/wireframes/mobile_home.png)

* Navbar Dropdown Display

![Mobile Navbar](documentation/wireframes/mobile_nav.png)

* Trip List Display

![Mobile Trip List](documentation/wireframes/mobile_triplist.png)

* Reservation List Display

![Mobile Reservation List](documentation/wireframes/mobile_reservation_list.png)

---

## Flowcharts

The flowchart was created to help to understand the application and its functionality.

The flowchart was created using [Figma](https://www.figma.com/).

- [Flowchart for Reservation](documentation/flowchart/flowchart_reservation.png)

---

## Information Architecture

### Database

* During the earliest stages of the project, the database was created using SQLite.
* The database was then migrated to PostgreSQL.

### Entity-Relationship Diagram

## Data Modeling

**Trip**

| Name           | Database Key   | Field Type    | Validation |
| -------------  | -------------  | ------------- | ---------- |
| Trip ID        | trip_id        | AutoField     | primary_key=True    |
| Trip Number    | trip_number    | CharField     | max_length=30, db_index=True    |
| Origin         | origin         | CharField     | max_length=30, db_index=True    |
| Destination    | destination    | CharField     | max_length=30, db_index=True    |
| Date           | date           | DateField     | db_index=True    |
| Time           | time           | TimeField     |   |
| Total Seats    | total_seats    | IntegerField  |   |    
| Available Seats| available_seats| IntegerField  |   |

**Reservation**

| Name           | Database Key   | Field Type    | Validation |
| -------------- | -------------- | ------------- | ---------- |
| User           | user           | ForeignKey    | User, on_delete=models.CASCADE|
| Trip ID        | trip_id (FK)   | ForeignKey    | Trip, on_delete=models.CASCADE|
| Number of Seats| number_of_seats| IntegerField  | default=1  |
| Date           | date           | DateField     |   |
| Time           | time           | TimeField     | null=True, blank=True|

## Relationships

- User to Reservation: One User can have many Reservations (one-to-many). This is represented by the user_id foreign key in the Reservation table.
- Trip to Reservation: One Trip can have many Reservations (one-to-many). This is represented by the trip_id foreign key in the Reservation table.

## Acknowledgments

- The Almighty for the opportunity to do coding.
- My family for their unending support.
- My other half for the love and understanding.
- Cici my girl for the inspiration.
- [Iuliia Konovalova](https://github.com/IuliiaKonovalova) my mentor for the advice, tips and guiding me through the project.
- [Code Institute](https://codeinstitute.net/) lessons, tutors and Slack community members for their support and help.
- [Slack overflow](https://stackoverflow.com/) and [MDN Web Docs](https://developer.mozilla.org/en-US/) for being my run-to references when I have questions. 

