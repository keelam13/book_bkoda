# Testing

## Manual Testing

Testing was done throughout site development, for each feature before it was merged into the master file.

Usability was tested with the below user acceptance testing, sent to new users to ensure testing from different users, on different devices and browsers to ensure issues were caught and where possible fixed during development.


|     | User Actions           | Expected Results | Y/N | Comments    |
|-------------|------------------------|------------------|------|-------------|
| Logo        |                        |                  |      |             |
| 1           | Clicks the logo or Home button in navbar.| Redirect to home page.| Y | | 
| Sign Up     |                        |                  |      |             |
| 1           | Click on Register button on the navbar| Redirection to Sign Up page | Y |          |
| 2           | Click on the sign up link in the instruction box | Redirection to Sign Up page | Y |          |
| 3           | Click on the signin link in the form | Redirection to Login page | Y |          |
| 4           | Enter valid email | Field will only accept email address format | Y |          |
| 5           | Enter valid username | Field will only accept no more than 50 characters | Y |          |
| 6           | Enter valid password | Field will only accept secure passwords | Y |          |
| 7           | Enter valid password confirmation | Field will only accept the same password from the previous field | Y |          |
| 8          | Click on the Sign Up button | Redirects to Home Page with pop-up confirming successful sign in. Resgister and Log In in navbar is now replaced by Logout | Y |          |
| 9          | Sign In with the same email/username and password | Redirects to Home Page with pop-up confirming successful sign in. Resgister and Log In in navbar is now replaced by Logout | Y |          |
| 10          | Click Logout | Takes user to log out page to confirm logout | Y |          |
| 11          | Click  SIgn out button  | Redirects user to home page | Y |          |
| Log In      |                        |                  |      |             |
| 1           | Click on Login button | Redirection to Login page | Y |          |
| 2           | Click on the SignUp link in the form | Redirection to SignUp page | Y |          |
| 3           | Enter valid email or username | Field will only accept email address format | Y |          |
| 4           | Enter valid password | Field will only accept secure passwords | Y |          |
| 5           | Click on the Sign In button | Redirect user to Home page with pop-up confirming successful sign in. Get started button now missing in main nav, replaced by Menu | Y |          |
| 5           | Clicks "Forgot Password" instead of "Sign In" | Redirects user to forgot password page | Y |          |
| My Reservation |                     |                  |      |             |
| 1           | Logged in User clicks the My Reservation link in the navbar.| Redirected to the users Reservation lists.| Y  |   |
| 2           | Not logged in user clicks the My Reservation link in the navbar.| Redirected to sign in page.| Y  |   |
| Search Trips|                        |                  |      |              |
| 1           | Enter Origin in Field. | Form will suggest origin, accepts only the available origins in the data.| Y  |   |
| 2           | Enter Destination in Field. | Form will suggest destinations, accepts only the available destination in the data.| Y  |   |
| 3           | Clicks on the calendar icon beside the Date field.| Caledar pops up for user to choose date.| Y  |   |
| 4           | Enter date in the date field.| Date format must be as the label suggests.| Y  |   |
| 5           | Clicks Search Trips button.| Takes to Trip List based on the search details.| Y  |   |
| Reservation | | | | |
| 1            | Logged in user clicks reserve button.| Takes to reservation form.| Y| |
| 2            | Not logged in user clicks reserve button.| Redirects to sign in page.| Y | |
| 3            | Enters number of seats and clicks reserve seats button.| Raises error if number is equal or less than 0, or in higher than available seats, else redirects to My Reservation with pop-up confirming successful Reservation.| Y | |
| 4            | Clicks the Back to trips button in the reservation form.| Calls confirmation.|Y | |
| 5            | Clicks "No".| Removes the Confirmation dialog.| Y | |
| 6            | Clicks "OK".| Redirects to the Trip list.| Y | |
| 7            | Clicks Previous Day button.| Takes to previous day trips, but if it's in the past it will raise an error.| Y | |
| 8            | Clicks the Next Day button.| Takes to next day trips, but will raise error if the are no trips available.| Y | |
| 9            | Clicks Edit Search button. | Rdirects to home page.| Y | |
| My Reservations | | | | |
| 1            | Clicks Update button.| Takes to Reservation Form for editing number of seats.| Y | |
| 2            | Clicks Reserve Seats in the form.| Number of seats is updated with pop-up confirming successful update.| Y | |
| 3            | Clicks Cancel/Delete button.| Takes to Cancelation confirmation dialog.| Y | |
| 4            | Clicks the "No" button.| Redirects to My Reservations.| Y | |
| 5            | Clicks "Yes" button.| Redirect to My Reservations with pop-up confirming successful cancelation.| Y | |
| 6            | Clicks Back to Home button.| Redirects to Home Page.| Y | |
| 7            | Trip goes the in past.| Update button will be replaced by "Past Trip", and Cancel button will be replaced with Delete button.| Y | |
| Social Media Icons | | | | |
| 1            | Click any of the icons.| Takes to the SocMed account.| Y | |
| 2            | Click email.| Opens email.| Y | |
| 3            | Clicks Phone Number.| Tries to call the Number.| Y | |



---

## Testing User Story

### **Searching and Viewing**
1 Passenger Search for trips Select one to book
2 Passenger View individual trip details Identify the route, date and time of departure and arrival, available seats, and the price

### **Registration and User Accounts**
3 Site User Easily register for an account Have a personal account and be able to view my profile
4 Site User Easily register with my social account Register with my Facebook or Gmail accounts
4 Site User Easily login or logout Access my personal account information
5 Site User Easily recover my password in case I forget it Recover access to my account
6 Site User Receive an email confirmation after registering Verify that my account registration was successful
7 Site User Have a personalized user profile View my personal trip history and booking confirmations, and save my payment information

### **Booking**
8 Passenger Easily select the trip that I want to book Ensure I don't accidentally select the wrong trip
9 Passenger Add the passengers Easily make changes before booking
10 Passenger Easily enter my payment information Check out quickly and with no hassles
11 Passenger Feel my personal and payment information is safe and secure Confidently provide the needed information to make a purchase
12 Passenger View an booking confirmation Verify that I haven't made any mistakes
13 Passenger Receive an email confirmation after payment Keep the confirmation of what I've paid for.
14 Passenger Easily manage my booking Change the date and/or time of my travel when I have to

### **Admin and Transport Management**
15 Manager Add a trip Add new trips to the list
16 Manager Easily see bookings Easily plan for the next trips

---

## Bugs
During the development of this app, there were a lot of bugs encountered and were fixed. Some were documented in the commits, but unfortunately some others not. Here are some of the bugs with their fixes:

* Bug: Widget placeholder after the 9th passenger is displaying "(Passenger 0), (Passenger 1)" and so on.
    Solution: Removed the second for loop that contained the regex logic and create the placeholder directly within the first for loop.

* Bug: The alert for null and unpaid bookings in the staff dashboard and bookings list are displaying the correct expired bookings counts but the cancel_null and _unpaid_bookings buttons are not cancelling the bookings as expected.
    Solution: Corrected the typo within the null_bookings filter, e.i payment_method_isnull=True changed to payment_method_type_isnull=True. 

* Bug: The refund for rescheduled bookings is being given in full, even if the original booking was close to the departure time and would have been charged with a fee.
    Solution: Added a code to check for original departure time if the booking being cancelled is not a new booking or have been rescheduled. The original departure time will be the basis for the refund calculation. This is also reflected in the booking policy.

* Bug: There is a horizontal overflow for smaller screens.
    Solutions: Separate the html from the body css style and gave its overflow-x property a hidden value. 

* Bug: The card brand and card last 4 is not being displayed in the Booking details.
    Solutions: Corrected another typo in the if block checking the payment method, e.i "CARD" changed to "card".

---

## Validation:


### HTML Validation:

All validated HTML but one is raising an error when passing through the official [W3C](https://validator.w3.org/) validator. However the error is coming from the allauth template and is not causing any problem in the signing up ang signing in processess. This checking was done manually by copying the view page source code (Ctrl+U) and pasting it into the validator. In Sign up Page the errors were


* Home Page

![Home Page](documentation/validation/home_page_w3c_validation.png)

 Signup Page

![Signup Page](documentation/validation/sign_up_w3c_validation.png)

* Login Page

![Login Page](documentation/validation/signin_page_w3c_validation.png)

* Logout Page

![Logout Page](documentation/validation/sign_out_page_w3c_validation.png)

* Reset Password Page

![Reset Password Page](documentation/validation/reset)

 Trip List Page

![Trip List Page](documentation/validation/)

 Reservation Form Page

![Reservation Form Page](documentation/validation/)

 Reservation List Page

![Reservation List Page](documentation/validation/)

 Cancel Reservation Page

![Cancel Reservation Page](documentation/validation/)


### CSS Validation:

- [Full CSS Validation Report]

- No errors or warnings were found when passing through the official [W3C (Jigsaw)]

### JS Validation:

- [Full JS Validation Report]

- No errors or warning messages were found when passing through the official [JSHint]

### Python Validation:

* Admin.py
- [Full Python Validation - Admin]

* Apps.py
- [Full Python Validation - Apps]

* ASGI.py
- [Full Python Validation - ASGI]

* Forms.py
- [Full Python Validation - Forms]

* Manage.py
- [Full Python Validation - Manage]

* Models.py
- [Full Python Validation - Models]

* Setting.py
- [Full Python Validation - Settings]

* URL.py
- [Full Python Validation - URL]

* Views.py
- [Full Python Validation - Views]

* WSGI.py
- [Full Python Validation - WSGI]

- No errors so far were found in the validated coeds through CI Python Linter [online validation tool](https://pep8ci.herokuapp.com/#). This checking was done manually by copying python code and pasting it into the validator.


---
## Lighthouse Report

* Home Page

![Home Page]

 Signup Page

![Signup Page]

* Login Page

![Login Page]

* Logout Page

![Logout Page]


---

## Compatibility

Testing was conducted on the following browsers;

- Chrome;

---

# Responsiveness

The responsiveness was checked manually by using devtools (Chrome) throughout the whole development.


---