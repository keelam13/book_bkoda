# book BKODA App - Features

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

---

# BKODA Transport - Booking Policy

- This policy outlines the terms and conditions for booking seats through the BKODA application for trips from Kabayan, Benguet to Baguio City and vice versa. By booking a seat, you agree to abide by the terms set forth below.

1. **Booking and Seat Reservation**

* Availability: Seat availability is on a first-come, first-served basis.
* Fare: The standard fare for a one-way trip from Kabayan, Benguet to Baguio City or vice versa is PHP 250.00. Please note that fares are subject to change without prior notice. The final fare will be displayed at the time of booking confirmation.
* Booking Confirmation: Your booking is considered confirmed only upon successful receipt of the full payment.

2. **Payment Options and Confirmation**

We offer the following convenient payment methods:

- Credit/Debit Card

    Payments made via credit or debit card are processed immediately.
    Upon successful card payment, your booking will be instantly confirmed. You will receive an immediate confirmation of your reservation.
    Payment Centers (Cash) / Money Wallet (e.g., GCash):


- If you choose to pay via a designated payment center (cash) or money wallet (e.g., GCash), your seat reservation will be held for a limited time.

    Payment Deadline: The full amount must be paid and verified by the earlier of these two conditions:
        a. Twenty-four (24) hours from the time of booking, OR
        b. Three (3) hours before the scheduled departure time of your trip.    
    Failure to Pay: If full payment is not received and verified by this deadline, your reservation will be automatically cancelled, and the seats will be released for other passengers to book.

3. **Discounts**

* Eligible Passengers: A 20% discount is available for:
    - Senior Citizens: Individuals aged 60 years old and above.
    - Students.
* Discount Application: The full standard fare is paid at the time of booking. The 20% discount will be processed as a refund.
* On-site Verification & Refund: To avail of the discount, eligible passengers must present a valid Senior Citizen ID or a valid School ID to the bus attendant on-site before boarding. Upon successful verification, the 20% discount amount will be refunded directly by the bus attendant.

4. **Cancellation Policy**

* Free Cancellation: If cancelling more than 24 hours before departure.
    - Action: Full refund.
* Late Cancellation (50% fee): If cancelling between 24 hours and 3 hours (inclusive) before departure.
    - Action: 50% refund, 50% fee deducted.
* Cancellation (No Refund): If cancelling less than or exactly 3 hours before departure.
    - Action: Booking status changes to CANCELED. No refund issued.
* NOTE: The cancellation refund percentage is determined by the time elapsed between the cancellation request and the original departure time of the booking. Any rescheduling of the trip does not change the cancellation refund policy.


5. **Rescheduling Policy**

* Free Rescheduling: If rescheduling more than 24 hours before original departure.
    - Action: No charge. Subject to seat availability.
* Late Rescheduling (15% fee): If rescheduling between 24 hours and 3 hours (inclusive) before original departure.
    - Action: 15% rescheduling charge applied. Subject to seat availability.
* No Rescheduling Allowed: If rescheduling less than 3 hours before original departure.

6. **Refunds**

* Refunds for eligible cancellations will be processed according to the original payment method. Please allow 2-3 business days for the refund to reflect in your account.
* For cash payments via payment centers, refunds will be processed either via GCash, bank transfer, or pickup at the office (all terminals).

7. **Changes to Schedules and Services**

* While we strive to maintain our published schedules, BKODA Transport reserves the right to modify, delay, or cancel trips due to unforeseen circumstances such as weather conditions, road closures, mechanical issues, or other operational necessities.
* In the event of a cancellation by BKODA Transport, affected passengers will be offered a full refund or the option to rebook for an alternative date/time, subject to availability.

8. **Passenger Responsibilities**

* It is the passenger's responsibility to ensure that all booking details (date, time, passenger names) are accurate at the time of booking.
* Passengers are advised to arrive at the designated pick-up point at least 30 minutes before the scheduled departure time.
* Passengers must present their confirmed booking reference or ticket (digital or printed) to the bus attendant before boarding.

