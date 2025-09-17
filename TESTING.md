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

Most HTMLs passed the official [W3C](https://validator.w3.org/) validator. However some errors were raised in
 a few pages. Some errors are coming from the allauth template and and the others from the Stripe elements and the limitation of its implementation.

The errors from the allauth templates are as follows:
    - Error: End tag p implied, but there were open elements.
    - Error: Unclosed element span.
    - Error: Stray end tag span.
    - Error: No p element in scope but a p end tag seen.

And the error from Stripe element implementations:
    - Error: The value of the for attribute of the label element must be the ID of a non-hidden form control.

These errors, however, are not causing any problem in the signing up ang signing in processess, and the overall functionality of the app. That is why I left it as is, and since I have not found a solution yet to correct the errors. This checking was done manually by copying the view page source code (Ctrl+U) and pasting it into the validator.


* Home Page

![Home Page](documentation/validation/home_page_w3c_validation.png)

* Signup Page

![Signup Page](documentation/validation/sign_up_page_w3c_validation.png)

* Confirm Email Page

![Confirm Email Page](documentation/validation/confirm_email_page_w3c_validation.png)

* Login Page

![Login Page](documentation/validation/signin_page_w3c_validation.png)

* Logout Page

![Logout Page](documentation/validation/sign_out_page_w3c_validation.png)

* Reset Password Page

![Reset Password Page](documentation/validation/reset_password_page_w3c_validation.png)

* Trip List Page

![Trip List Page](documentation/validation/trip_search_result_w3c_validation.png)

* Reschedule Trip List Page

![Reschedule Trip List Page](documentation/validation/reschedule_trip_search_results_w3c_validation.png)

* Booking Form Page

![Booking Form Page](documentation/validation/booking_form_w3c_validation.png)

* Payment Form Page

![Payment Form Page](documentation/validation/payment_form_page_w3c_validation.png)

* My Booking Confirmation Page

![My Booking Confirmation Page](documentation/validation/booking_confirmation_page_w3c_validation.png)

* My Account Page

![My Account Page](documentation/validation/my_account_page_w3c_validation.png_)

* My Account Details Page (My Account)

![My Account Details Page](documentation/validation/account_details_page_w3c_validation.png)

* Personal Information Page (My Account)

![Personal Info Page](documentation/validation/personal_info_page_w3c_validation.png)

* My Bookings Page (My Account)

![My Bookings Page](documentation/validation/my_bookings_page_w3c_validation.png)

* Bookings List Page (Manage Booking)

![Bookings List Page](documentation/validation/manage_all_bookings_w3c_validation.png)

* Booking Details (Manage Booking)

![Booking Details Page](documentation/validation/manage_booking_details_page_w3c_validation.png)

* Confirmed Bookings Page (Manage Booking)

![Confirmed Bookings Page](documentation/validation/manage_confirmed_bookings_page_w3c_validation.png)

* Pending Bookings Page (Manage Booking)

![Pending Bookings Page](documentation/validation/manage_pending_page_w3c_validation.png)

* Refund Bookings Page (Manage Booking)

![Refund Bookings Page](documentation/validation/manage_refund_page_w3c_validation.png)

* Cancelled Bookings Page (Manage Booking)

![Cancelled Bookings Page](documentation/validation/manage_canceled_w3c_validation.png)

* Confirm Booking Reschedule Page (Manage Booking)

![Confirm Booking Reschedule Page](documentation/validation/confirm_resched_page_w3c_validation.png)

* Confirm Booking Cancellation Page (Manage Booking)

![Confirm Booking Cancellation Page](documentation/validation/confirm_cancellation_page_w3c_validation.png)

* Staff App Dashboard Page

![Bookings List Page](documentation/validation/staff_dashboard_page_w3c_validation.png)

* Trips List Page (Staff App)

![Tripss List Page](documentation/validation/staff_trips_page_w3c_validation.png)

* Bookings List Page (Staff App)

![Bookings List Page](documentation/validation/staff_bookings_page_w3c_validation.png)



### CSS Validation:

No errors or warnings were found when passing through the official [W3C (Jigsaw)](https://jigsaw.w3.org/css-validator/)

* Base CSS

![Base CSS](documentation/validation/base_css_w3c_validation.png)

* Bookings Form CSS

![Bookings Form](documentation/validation/booking_form_css_w3c_validation.png)

* Staff App

![Staff App](documentation/validation/staff_app_css_w3c_validation.png)


### JS Validation:

No errors or warning messages were found when passing through the official [JSHint](https://jshint.com/)

* Base JS

![Base JS](documentation/validation/base_js_validation.png)

* Payment Page JS

![Payment Page JS](documentation/validation/payment_page_js_validation.png)

* Custom Country Select Widget JS

![Custom Country Select Widget JS](documentation/validation/country_widget_js_validation.png)



### Python Validation:

No errors so far were found in the validated codes through CI Python Linter [online validation tool](https://pep8ci.herokuapp.com/#). This checking was done manually by copying python code and pasting it into the validator.


* Admin.py
- ![Pep8 Validation - Booking Admin](documentation/validation/booking_admin_pep8_validation.png)
- ![Pep8 Validation - Trips Admin](documentation/validation/trips_admin_pep8_validation.png)

* Apps.py
- ![Pep8 Validation - Booking Apps](documentation/validation/booking_apps_pep8_validation.png)
- ![Pep8 Validation - Home Apps](documentation/validation/home_apps_pep8_validation.png)
- ![Pep8 Validation - Manage Booking Apps](documentation/validation/manage_apps_pep8_validation.png)
- ![Pep8 Validation - My Account Apps](documentation/validation/my_account_apps_pep8_validation.png)
- ![Pep8 Validation - Staff App Apps](documentation/validation/staff_apps_pep8_validation.png)
- ![Pep8 Validation - Trips Apps](documentation/validation/trips_apps_pep8_validation.png)

* ASGI.py
- ![Pep8 Validation - BKODA ASGI](documentation/validation/bkoda_asgi_pep8_validation.png)

* Forms.py
- ![Pep8 Validation - Booking Forms](documentation/validation/booking_forms_pep8_validation.png)
- ![Pep8 Validation - My Account Forms](documentation/validation/my_account_forms_pep8_validation.png)
- ![Pep8 Validation - Staff App Forms](documentation/validation/staff_forms_pep8_validation.png)
- ![Pep8 Validation - Trips Forms](documentation/validation/trips_forms_pep8_validation.png)

* Manage.py
- ![Pep8 Validation - Staff App Cancel Abandoned Bookings](documentation/validation/staff_manage_cancel_abandoned_pep8_validation.png)
- ![Pep8 Validation - Staff App Generate Trips](documentation/validation/staff_manage_generate_pep8_validation.png)

* Models.py
- ![Pep8 Validation - Booking Models](documentation/validation/booking_models_pep8_validation.png)
- ![Pep8 Validation - My Account Models](documentation/validation/my_account_models_pep8_validation.png)
- ![Pep8 Validation - Trips Models](documentation/validation/trips_models_pep8_validation.png)

* Setting.py
- ![Pep8 Validation - BKODA Settings](documentation/validation/bkoda_settings_pep8_validation.png)

* Signals.py
- ![Pep8 Validation - My Account Signals](documentation/validation/my_account_signals_pep8_validation.png)

* Templatetags
- ![Pep8 Validation - Booking Filters](documentation/validation/booking_filters_pep8_validation.png)
- ![Pep8 Validation - Trips Filters](documentation/validation/trips_filters_pep8_validation.png)

* URL.py
- ![Pep8 Validation - BKODA URLs](documentation/validation/bkoda_urls_pep8_validation.png)
- ![Pep8 Validation - Booking URLs](documentation/validation/booking_urls_pep8_validation.png)
- ![Pep8 Validation - Home URLs](documentation/validation/home_urls_pep8_validation.png)
- ![Pep8 Validation - Manage Booking URLs](documentation/validation/manage_urls_pep8_validation.png)
- ![Pep8 Validation - My Account URLs](documentation/validation/my_account_urls_pep8_validation.png)
- ![Pep8 Validation - Staff App URLs](documentation/validation/staff_urls_pep8_validation.png)
- ![Pep8 Validation - Trips URLs](documentation/validation/trips_urls_pep8_validation.png)

* Utils.py
- ![Pep8 Validation - Booking Utils](documentation/validation/booking_utils_pep8_validation.png)
- ![Pep8 Validation - Manage Booking Utils](documentation/validation/manage_utils_pep8_validation.png)
- ![Pep8 Validation - Staff App Utils](documentation/validation/staff_utils_pep8_validation.png)

* Views.py
- ![Pep8 Validation - BKODA Views](documentation/validation/bkoda_views_pep8_validation.png)
- ![Pep8 Validation - Booking Views](documentation/validation/booking_views_pep8_validation.png)
- ![Pep8 Validation - Home Views](documentation/validation/home_views_pep8_validation.png)
- ![Pep8 Validation - Manage Booking Views](documentation/validation/manage_views_pep8_validation.png)
- ![Pep8 Validation - My Account Views](documentation/validation/my_account_views_pep8_validation.png)
- ![Pep8 Validation - Staff App Views](documentation/validation/staff_views_pep8_validation.png)
- ![Pep8 Validation - Trips Views](documentation/validation/trips_views_pep8_validation.png)

* WSGI.py
- ![Pep8 Validation - BKODA WSGI](documentation/validation/bkoda_wsgi_pep8_validation.png)

---
## Lighthouse Report

The lighthouse reports suggests that the book BKODA App needs more improvements in the Performance and in the Best Practices categories. Overall, the web app needs fine tuning to improve its quality across several categories.
    - In the Performance category for pages needing more improvements:
        1. Red Metrics: Significant Issues
            - First Contentful Paint (FCP): 4.0 s
            - Largest Contentful Paint (LCP): 4.2 s

        2. Yellow/Orange Metrics: Needs Improvement
            - Total Blocking Time (TBT): 490 ms
            - Speed Index: 5.1 s

        3. Green Metrics: Good
            - Cumulative Layout Shift (CLS): 0.088

    - In the Best Practices category for pages needing more improvements:
        Key Issues:
        1. Uses third-party cookies — 12 cookies found:
            - mailchimp
            - _stripe_orig_uat

        2. Issues were logged in the Issues panel in Chrome Devtools:
            - A form field (from the MailChimp embedcode) has an id or name attribute that the browser's autofill recognizes. However, it doesn't have an autocomplete attribute assigned. This might prevent the browser from correctly autofilling the form.

* Home Page

    - Home Page Desktop
    ![Home Page Desktop](documentation/lighthouse/lh_home_desktop.png)
    - Home Page Mobile
    ![Home Page Mobile](documentation/lighthouse/lh_home_mobile.png)

* Trip List (Search Result) Page

    - Trip List Page Desktop
    ![Trip List Page Desktop](documentation/lighthouse/lh_trip_list_desktop.png)
    - Trip List Page Mobile
    ![Trip List Page Mobile](documentation/lighthouse/lh_trip_list_mobile.png)

* Confirm Booking Page

    - Booking Form Page Desktop
    ![Booking Form Page Desktop](documentation/lighthouse/lh_booking_form_desktop.png)
    - Booking Form Page Mobile
    ![Booking Form Page Mobile](documentation/lighthouse/lh_booking_form_mobile.png)

* Booking Payment Page

    - Payment Form Page Desktop
    ![Payment Form Page Desktop](documentation/lighthouse/lh_payment_form_desktop.png)
    - Payment Form Page Mobile
    ![Payment Form Page Mobile](documentation/lighthouse/lh_payment_form_mobile.png)

* My Bookings Page

    - My Bookings Form Page Desktop
    ![My Bookings Page Desktop](documentation/lighthouse/lh_my_bookings_desktop.png)
    - My Bookings Page Mobile
    ![My Bookings Page Mobile](documentation/lighthouse/lh_my_bookings_mobile.png)

* My Account Page

    - My Account Form Page Desktop
    ![My Account Page Desktop](documentation/lighthouse/lh_my_account_desktop.png)
    - My Account Page Mobile
    ![My Account Page Mobile](documentation/lighthouse/lh_my_account_mobile.png)

* Staff App Page

    - Staff App Form Page Desktop
    ![Staff App Page Desktop](documentation/lighthouse/lh_staff_app_desktop.png)
    - Staff App Page Mobile
    ![Staff App Page Mobile](documentation/lighthouse/lh_staff_app_mobile.png)

---

## Compatibility

The app was developed using Chrome browser. To check for compatibility, testing was conducted on the following browsers:

- Edge
    - Home
    ![Home Edge](documentation/compatibility/edge_home.png)

    - Booking Confirmation
    ![Booking Confirmation Edge](documentation/compatibility/edge_booking_confirmation.png)

    - My Account
    ![My Account Edge](documentation/compatibility/edge_my_account.png)

    - My Bookings
    ![My Bookings Edge](documentation/compatibility/edge_my_bookings.png)

    - Staff App
    ![Staff App Edge](documentation/compatibility/edge_staff_app.png)

- Mozilla
    - Home
    ![Home Mozilla](documentation/compatibility/mozilla_home.png)

    - Booking Confirmation
    ![Booking Confirmation Mozilla](documentation/compatibility/mozilla_booking_confirmation.png)

    - My Account
    ![My Account Mozilla](documentation/compatibility/mozilla_my_account.png)

    - Manage Bookings
    ![Manage Bookings Mozilla](documentation/compatibility/mozilla_manage_bookings.png)

    - Staff App
    ![Staff App Mozilla](documentation/compatibility/mozilla_staff_app.png)

---

# Responsiveness

The responsiveness was checked manually by using devtools (Chrome) throughout the whole development. A Mobilephone (Oppo F1) was used to take the mobile screenshots. 

* Home Page
    - Desktop
        + Authenticated User
      ![Authenticated](documentation/responsiveness/desktop_home_auth.png)
        + Unauthenticated User
      ![Unauthenticated](documentation/responsiveness/desktop_home_unauth.png)
    
    - Mobile
        + Authenticated User
      ![Authenticated](documentation/responsiveness/mobile_home_auth.png)
        + Unauthenticated User
      ![Unauthenticated](documentation/responsiveness/mobile_home_unauth.png)

* Sign In Page
    - Desktop
    ![Signin Desktop](documentation/responsiveness/desktop_signin.png)

    - Mobile
    ![Signin  Mobile](documentation/responsiveness/mobile_signin.png)

* Sign Up Page
    - Desktop
    ![Desktop Sign Up](documentation/responsiveness/desktop_signup.png)

    - Mobile
    ![Mobile Sign Up](documentation/responsiveness/mobile_signup.png)

* Trip List
    - Desktop
    ![Desktop Trip List](documentation/responsiveness/desktop_triplist.png)

    - Desktop (Reschedule)
    ![Desktop Trip List for Resched](documentation/responsiveness/desktop_resched_triplist.png)

    - Mobile
    ![Mobile Trip List](documentation/responsiveness/mobile_triplist.png)
    
    - Mobile (Reschedule)
    ![Mobile Trip List for Resched](documentation/responsiveness/mobile_resched_triplist.png)

* Booking Confirmation
    - Desktop
    ![Desktop Booking Confirmation](documentation/responsiveness/desktop_confirm_booking.png)

    - Mobile
    ![Mobile Booking Confirmation](documentation/responsiveness/mobile_confirm_booking.png)

    - Confirm Cancel
    ![Mobile Cancel Booking](documentation/responsiveness/mobile_confirm_booking_cancel.png)

* Payment Form
    - Desktop
    ![Desktop Payment Form](documentation/responsiveness/desktop_payment_form.png)

    - Desktop
    ![Desktop Payment Form](documentation/responsiveness/desktop_payment_form.png)

    - Mobile
    ![Mobile Payment Form](documentation/responsiveness/mobile_payment_form.png)

    - Card Payment
    ![Mobile Card Payment](documentation/responsiveness/mobile_card_payment.png)

    - Cash Payment
    ![Mobile Cash Payment](documentation/responsiveness/mobile_cash_payment.png)

    - Card Payment
    ![Mobile GCash Payment](documentation/responsiveness/mobile_gcash_payment.png)

    - Spinning Overlay
    ![Desktop Spinning Overlay](documentation/responsiveness/desktop_spinning_overlay.png)

* Booking Confirmation
    - Desktop
        - Authenticated User
    ![Desktop Booking Confirmation 1](documentation/responsiveness/desktop_booking_confirmed_auth.png)
        - Unauthenticated User
    ![Desktop Booking Confirmation 2](documentation/responsiveness/desktop_booking_confirmed_unauth.png)

    - Mobile
        - Authenticated User
    ![Mobile Booking Confirmation 1](documentation/responsiveness/mobile_booking_confirmed.png)

* Pending Payment
    - Desktop
    ![Desktop Pending Payment](documentation/responsiveness/desktop_pending_payment_auth.png)

    - Mobile
    ![Mobile Pending Payment](documentation/responsiveness/mobile_pending_payment.png)

* My Account
    - Desktop
        - My Account (Non-Staff)
    ![Desktop My Account](documentation/responsiveness/desktop_my_account.png)

        - My Account (Staff)
    ![Desktop My Account - Staff](documentation/responsiveness/desktop_my_account_staff.png)

    - Mobile
        - My Account (Non-Staff)
    ![Mobile My Account](documentation/responsiveness/mobile_my_account.png)

        - My Account (Staff)
    ![Mobile My Account - Staff](documentation/responsiveness/mobile_my_account_staff.png)

* Personal Information
    - Desktop
    ![Desktop Personal Info](documentation/responsiveness/desktop_personal_info.png)

    - Mobile
    ![Mobile Personal Info](documentation/responsiveness/mobile_personal_info.png)

* My Bookings
    - Desktop
    ![Desktop My Bookings](documentation/responsiveness/desktop_my_boookings.png)

    - Mobile
    ![Mobile My Bookings](documentation/responsiveness/mobile_my_bookings.png)

* Booking Details
    - Desktop
    ![Desktop Booking Details](documentation/responsiveness/desktop_booking_details.png)

    - Mobile
    ![Mobile Booking Details](documentation/responsiveness/mobile_booking_details.png)

* Manage Bookings
    - Desktop
    ![Desktop Manage Booking](documentation/responsiveness/desktop_manage_booking.png)

    - Mobile
    ![Mobile Manage Booking](documentation/responsiveness/mobile_manage_booking.png)

* Reschedule Booking
    - Desktop
    ![Desktop Reschedule Booking](documentation/responsiveness/desktop_confirm_resched.png)

    - Mobile
    ![Mobile Reschedule Booking](documentation/responsiveness/mobile_confirm_resched.png)

* Cancel Booking
    - Desktop
    ![Desktop Cancel Booking](documentation/responsiveness/desktop_confirm_booking_cancel.png)

    - Mobile
    ![Mobile Cancel Booking](documentation/responsiveness/mobile_confirm_booking_cancel.png)

* Staff App Dashboard
    - Desktop
    ![Desktop Staff App - Dashboard](documentation/responsiveness/desktop_staff_dashboard.png)

    - Mobile
    ![Mobile Staff App](documentation/responsiveness/mobile_staff_dashboard.png)

* Staff App Trip List
    - Desktop
    ![Desktop Staff App - Trips](documentation/responsiveness/desktop_staff_trips.png)

        - Trip Details
    ![Desktop Trip Details](documentation/responsiveness/desktop_trips_details.png)
    
    - Mobile
    ![Mobile Staff App](documentation/responsiveness/mobile_staff_trips.png)

        - Generate Trip Confirmation
    ![Mobile Genetrate Trip](documentation/responsiveness/mobile_staff_generate_trips.png)

* Staff App Booking List
    - Desktop
    ![Desktop Staff App - Bookings](documentation/responsiveness/desktop_staff_bookings.png)

        - Booking Details
    ![Desktop Booking Details](documentation/responsiveness/desktop_staff_booking_details.png)

    - Mobile
    ![Mobile Staff App](documentation/responsiveness/mobile_staff_bookings.png)

        - Cancel Abandoned Bookings
    ![Mobile Cancel Abandoned Booking](documentation/responsiveness/mobile_confirm_cancel_abandoned.png)

---