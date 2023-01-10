"""
Notify expiring users from Alma (ExLibris): main program
Copyright (C) 2023 - AK Bibliothek Wien
                     (Michael Birkner <michael.birkner@akwien.at>)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import datetime
import requests
import xml.etree.ElementTree as ET
import functions as fn
from string import Template
from time import sleep
from config import config

# Get a logger
logger: logging.Logger = fn.get_logger(
    log_level=config.get('log_level', 'INFO'),
    log_file=config.get('log_file', None))

# Check for mandatory configs
fn.check_mandatary_configs(config, logger)

# Set some variables based on the config file
today = datetime.date.today()
days_to_add = config.get('days_to_add', 14)
future_expiry_date = today + datetime.timedelta(days=days_to_add)
date_format = config.get('date_format', '%Y-%m-%d')
limit = config.get('limit', 100)
email_pause = config.get('email_pause', None)
api_base_path = str(config['api_base_path']).rstrip('/')
api_path = api_base_path + '/analytics/reports'
api_key = str(config['api_key'])
path = str(config['path'])
filter_template = Template(config['filter'])
filter_for_api = filter_template.substitute(
    today=today,
    future_expiry_date=future_expiry_date)

# Set URL params for API call
api_params = {
    'path': path,
    'filter': filter_for_api,
    'limit': limit,
    'col_names': 'false',
    'apikey': api_key
}

# Start logging
logger.info('---------------------------------------')
logger.info('Processing users expiring on ' + str(future_expiry_date))

# Variable to hold data of all users that should be notified
users_to_notify = []

# Create some vars for loop control
resumption_token = None
first_run = True

# Get user data from Analytics API and collect them in a list. As these
# could be paged, we use a "while loop": Always execute the first loop
# iteration because the while condition is True.
logger.info('Getting user data from Alma Analytics API')
while True:
    # Execute the API request and get the result
    result = requests.get(url=api_path, params=api_params,
                          headers={'accept': 'application/xml'})

    logger.info(
        'Calling Analytics API at ' + str(result.url) + ' with a limit of '
        + str(limit) + ' results per call')

    if (result.status_code >= 200 and result.status_code < 300):
        # Parse result body to XML object
        xml = ET.fromstring(result.text)

        # Check if there are more pages or just one
        is_finished = xml.findtext('QueryResult/IsFinished')

        # Get the resumption token if there are more pages
        if first_run:
            resumption_token = xml.findtext('QueryResult/ResumptionToken')

        # Iterate through rows and collect the data
        for row in xml.findall('QueryResult/ResultXml/{*}rowset/{*}Row'):
            first_name = row.findtext('{*}'
                + config['col_mapping']['first_name'])
            last_name = row.findtext('{*}'+config['col_mapping']['last_name'])
            email = row.findtext('{*}'+config['col_mapping']['email'])
            expiry_date = row.findtext('{*}'
                + config['col_mapping']['expiry_date'])

            logger.debug(
                'Getting user data. First name: ' + str(first_name)
                + ', Last name: ' + str(last_name) + ', Email: ' + str(email)
                + ', Expiry date: ' + str(expiry_date))

            # Check if we have an email adress and an expiry date. If
            # yes, collect the users data.
            if (email.strip() != '' and expiry_date.strip() != ''):
                users_to_notify.append({
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'expiry_date': expiry_date})
                
        # If "is_finished" is "true", stop further executions. If it is
        # "false", we get further user data by using the resumption
        # token.
        condition = False if (is_finished == 'true') else True

        # Execute further downloads (is_finished = false)
        if condition == True:
            # Clear all API parameters as the resumption token is the
            # only one we will need for paging
            api_params.clear()
            # Set resumption token and API key to API parameters
            api_params['token'] = resumption_token
            api_params['apikey'] = api_key
            # Set first_run to False. This avoids getting the resumption
            # token another time which would result in None, because the
            # token is available only on the first page of the results.
            first_run = False
        
        # Stop execution (is_finished = true)
        if condition == False:
            break
    else:
        logger.error(
            'Error when calling Analytics API at ' + str(result.url)
            + '. HTTP Status code: ' + str(result.status_code))

# Get the number of users that should be notified
no_of_users_to_notify = len(users_to_notify)

if no_of_users_to_notify > 0:
    logger.info(
        'Sending notification e-mails to ' + str(no_of_users_to_notify)
        + ' users')

    for user_to_notify in users_to_notify:
        user_to_notify: dict

        # Set some variables
        to_mail = user_to_notify['email'] \
            if config.get('to_email_test', None) is None \
            else config['to_email_test']
        alma_expiry_date = user_to_notify.get('expiry_date', None)
        first_name = user_to_notify.get('first_name', None)
        first_name = str(first_name
            if first_name is not None and
            first_name.strip() != '' else '')
        last_name = user_to_notify.get('last_name', None)
        last_name = str(last_name
            if last_name is not None and
            last_name.strip() != '' else '')
        full_name = ' '.join(filter(None, [first_name, last_name]))

        # Make sure that the user really has an expiry date as
        # calculated above. This could prevent mass sending of e-mails
        # if e. g. the filter for the Analytics API doesn't work and all
        # Alma users would be returned from the API call.
        if (alma_expiry_date == str(future_expiry_date)):       
            logger.debug(
                'Sending notification to ' + full_name + ' (e-mail: ' + to_mail
                + ', expiry date: ' + future_expiry_date.strftime(date_format)
                + ')')

            # Send email and set "notified_at" to the current date
            fn.send_mail(
                first_name,
                last_name,
                future_expiry_date,
                date_format,
                to_mail,
                config['from_email'],
                config['mail_subject'],
                config['mail_body']
            )

            # Wait some time between the transmissions of the e-mails if
            # configured to do so.
            if email_pause is not None and fn.is_number(email_pause):
                sleep(float(email_pause))
        else:
            logger.debug(
                'Can\'t send e-mail to ' + str(to_mail)+ ' because expiry date'
                + ' in Alma ('+str(alma_expiry_date)+') is not the same as the'
                + ' calculated expiry date ('+str(future_expiry_date)+')')
else:
    logger.info(
        'There are no users expiring on ' + str(future_expiry_date) + '. No'
        + ' users have to be notified; no e-mail will be sent.')
