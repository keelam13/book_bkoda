# BKODA Seat Booking App - Features

## Application Pages

The application includes the following pages:

- Home page
- Login page
- Registration page
- Logout page
- Trip Selection Page
- Reschdule Trip Page
- Cancel Trip Page
- Booking Form Page
- Payment Form Page
- My Account Page (Passenger)
- Staff Panel Page (Admin)

## Access to Pages by User Role

| Page Name                   | Passenger | Admin |
| --------------------------- | --------- | ----- |
| Home page                   | Y         | Y     |
| Login page                  | Y         | Y     |
| Registration page           | Y         | Y     |
| Logout page                 | Y         | Y     |
| Trip Selection Page         | Y         | Y     |
| Reschedule Trip Page        | Y         | Y     |
| Cancel Trip Page            | Y         | Y     |
| Booking Form Page           | Y         | Y     |
| Payment Form Page           | Y         | Y     |
| My Account Page             | Y         | Y     |
| Staff Panel Page            | N         | Y     |

- Each page has a consistent navbar and footer.

## Navbar

- **Home page link:** Directs users to the application's homepage.
- **Login/Registration button:** Provides access to login and registration functionalities.
- **Logo:** Displays the application's logo.
- **My Account:** Displays the user'S account details, profile info and bookings.
- **Staff Panel:** For staff members, they have additional navbar menu for trip management
- **Logout:** Logs user out of the application.

## Footer

- **Contact Information:** Includes relevant contact details (email and phone).
- **Social Media Account:** Links to the BKODA's social media accounts.
- **Responsive design:** Adapts to mobile and desktop views.
- **Newsletter Subscription:** Where users may subscribe to receive monthly newsletters.

## Home Page

- **Welcome Message:** Greets users and provides a brief overview of the application.
- **"Sign Up" link:** Links to the registration page.
- **Benefits Section:** Highlights key features and advantages of using the application.
- **Call to Action:** Encourages users to sign up and begin booking.

## Registration Page

- **Sign-up Form:** Collects user information (email, username, password).
- **Form Validation:** Ensures correct data entry.
- **"Login" Link:** Redirects users to the login page.

## Login Page

- **Login Form:** Collects username/email and password.
- **"Sign In" Button:** Authenticates users and redirects them to the appropriate page.
- **"Forgot Password?" Link:** Redirects users to the password reset page.
- **"Sign Up" Link:** Redirects users to the registration page.

## Logout Page

- **Confirmation Message:** Asks users to confirm logout.
- **"Sign Out" Button:** Logs users out and redirects them to the home page.


## Trip Selection Page

- **Search Functionality:** Allows users to search for trips by origin, destination, and date. Bothe for initial and rescheduling.
- **Trip List:** Displays available trips with details (route, date, time, total seats).
- **Seat Availability:** Shows the number of available seats for each route.
- **Reserve Button:** Displays the Booking Form Page

## Booking Form Page

- **Seat Booking:** Allows users to enter desired number of seats/ passengers.
- **Form validation:** Checks the entered number of seat against the available seats, checks if the number entered is lower or equal to zero, and if the entered number of seat is greater than the total seats and raises an error.

## Booking List Page (Passenger)

- **Booking:** Displays a list of the all the user's booking.
- **Booking Details:** Allows users to view details of each reservation.
- **Reschedule Booking:** Allows users to reschedule the trip, T&C apply.
- **Cancel Booking:** Allows users to cancel their booking, T&C apply.

## Booking List Page (Admin)

- **All Booking:** Displays a list of all bookings.
- **Booking Details:** Allows admins to view details of each booking.
- **Modify Booking:** Allows admins to make changes to bookings.
- **Cancel Booking:** Allows admins to cancel bookings.

## Admin Trip Management Page

- **Generate Trips:** Allows admins to add new trips.
- **Edit Route:** Allows admins to edit existing trip details (Route, date, time, seats).
- **Delete Route:** Allows admins to remove trips.

This document outlines the core features and functionalities of the Transportation Seat Booking App.

* Trips search.
* Booking management (view, update seats, cancel).
* User authentication (registration, login).
* Admin panel for route, schedule, and seat management.
* Responsive design.