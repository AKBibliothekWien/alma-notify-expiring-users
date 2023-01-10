"""
Notify expiring users from Alma (ExLibris): config file
Copyright (C) 2023 - AK Bibliothek Wien
                     (Michael Birkner <michael.birkner@akwien.at>)
                     
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

config = {
    # The base path to your Alma API
    'api_base_path': 'https://api-na.hosted.exlibrisgroup.com/almaws/v1',
    # An API key that has read access to the Analytics API of your Alma system
    'api_key': 'YOUR_API_KEY_WITH_READ_ACCESS_TO_ANALYTICS_API',
    # Path to an Analytic report with user data. The report should contain at least these fields: First Name, Last Name, Preferred Email, Expiry Date.
    # IMPORTANT: Set an "is prompted" filter on the "Expiry Date" field. Without that, the "filter" below won't work!
    # Save the report to a subfolder of the "Shared Folder" (probably the one accessible by your institution). To get the path to the report, open the
    # saved report from your catalog, inspect the URL in the address field of your browser and find value of the "path" parameter.
    'path': '/shared/My Institution/Reports/users_expiry_date',
    # A filter that gets users with an expiry date that lies N days in the future from today on.
    # See config "days_to_add" where you can set the number of days that should be added to todays date.
    # You can probably leave this filter as it is.
    'filter': '<sawx:expr xsi:type="sawx:comparison" op="equal" xmlns:sawx="com.siebel.analytics.web/expression/v1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><sawx:expr xsi:type="sawx:sqlExpression">"User Details"."Expiry Date"</sawx:expr><sawx:expr xsi:type="xsd:date">$future_expiry_date</sawx:expr></sawx:expr>',
    # Number of users in the result. Min. 25, max. 1000. Should be divisible by 25 (see also documentation of Alma Analytics API).
    # If there are more users, the result will be paged through with a resumption token so that all users will be received.
    'limit': 100,
    # Number of days that will be added to todays date. The result (future_expiry_date) will be used in the "filter" config above.
    # All users with the resulting expiry date will receive the notification.
    'days_to_add': 14,
    # The mapping of the columns from the API result. For getting the columns, try out the "Retrieve Analytics report" on the ExLibris Developer Network
    # with the report path you set above under "path" and inspect the result. Then set the mapping for these fields: first_name, last_name, email, expiry_date
    'col_mapping': {
        'first_name': 'Column3',
        'last_name': 'Column4',
        'email': 'Column1',
        'expiry_date': 'Column2'
    },
    # The "from" address from which the notification e-mail will be sent to the user
    'from_email': 'my_institution@example.com',
    # This is for testing. If you want to test the functionality of this script without sending e-mails to real users, you can set a test e-mail-address here.
    # All e-mails that would normally be sent to the users will be sent to this address instead. Comment out or set to None for deactivating the test e-mail and
    # sending the notifications to real users.
    'to_email_test': 'my_test_email_address@example.com',
    # Add a pause in seconds (could also be fractional seconds, e. g. 0.5 for half a second) between the transmissions of the e-mails. This is to avoid
    # too much load on you mail transfer agent if sending a lot of mails. Comment out or set to None for no pause.
    'email_pause': 0.5,
    # Log level for the logger. Default is INFO. Set to DEBUG for more information.
    'log_level': 'INFO',
    # Path to a file to which the log messages should be written (additionally to the console). Comment out or set to None to disable logging to a file.
    'log_file': 'notification.log',
    # Specify how the date format should look in the notification e-mails. Use %d for day of month, %m for month and %Y for year. Example: %d-%m-%Y.
    'date_format': '%d.%m.%Y',
    # The subject of the notification e-mail. You can use these variables: {first_name}, {last_name} and {expiry_date}.
    'mail_subject': 'Your account at My Institution expires at {expiry_date}',
    # The body of the notificytion e-mail. Use HTML for formatting. You can use these variables: {first_name}, {last_name} and {expiry_date}.
    'mail_body': '''\
        <html>
            <body>
                <p>Dear {first_name} {last_name}!</p>
                <p>Your account at My Institution expires at {expiry_date}.</p>
                <p>Please contact our staff to renew your account for being able to use our services in future.</p>
                <p>Best regards</p>
                <p>
                    My Institution<br />
                    My Address 123<br />
                    City 4567
                    My Telephone
                    My E-Mail
                </p>
            </body>
        </html>
    '''
}
