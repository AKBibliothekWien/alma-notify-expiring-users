"""
Notify expiring users from Alma (ExLibris): helper function
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

import sys
import logging
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging.handlers import RotatingFileHandler


def get_logger(log_level: str = None, log_file: str = None) -> logging.Logger:
    """
    Create a logger and return it
    """

    # Prepare logging
    logger = logging.getLogger('notify-expiring-users-logger')
    logger.setLevel(log_level if log_level is not None else 'INFO')
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)-5s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    # "Logging to file" handler
    if log_file is not None:
        rotating_file_handler = RotatingFileHandler(
            log_file,
            maxBytes=500000,
            backupCount=5)
        rotating_file_handler.setFormatter(formatter)
        logger.addHandler(rotating_file_handler)
    # "Logging to console" handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def send_mail(first_name: str, last_name: str, expiry_date: datetime.date,
              date_format: str, to_mail: str, from_mail: str, mail_subject:str,
              mail_body: str):
    """
    Send an HTML email
    """    

    first_name_clean = str(
        first_name if first_name is not None and
        first_name.strip() != '' else '')
    last_name_clean = str(
        last_name if last_name is not None and last_name.strip() != '' else '')
    expiry_date_formatted = expiry_date.strftime(date_format)
    mail_subject_formatted = mail_subject.format(
        first_name=first_name_clean,
        last_name=last_name_clean,
        expiry_date=expiry_date_formatted)
    mail_body_formatted = mail_body.format(
        first_name=first_name_clean,
        last_name=last_name_clean,
        expiry_date=expiry_date_formatted)

    # Remove two consecutive spaces from mail subject and mail body
    # (e. g. when first_name is empty)
    mail_subject_normalized = ' '.join(mail_subject_formatted.split('  '))
    mail_body_normalized = ' '.join(mail_body_formatted.split('  '))

    msg = MIMEMultipart()
    msg['To'] = to_mail
    msg['From'] = from_mail
    msg['Sender'] = from_mail
    msg['Reply-To'] = from_mail
    msg['Subject'] = f'{mail_subject_normalized}'
    msg.attach(MIMEText(mail_body_normalized, 'html'))

    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

def check_mandatary_configs(config: dict, logger: logging.Logger):
    """
    Check for mandatary configs
    """

    try:
        config['filter']
    except:
        logger.error('Mandatory config "filter" is not set!')
        sys.exit(1)
    try:
        config['api_base_path']
    except:
        logger.error('Mandatory config "api_base_path" is not set!')
        sys.exit(1)
    try:
        config['api_key']
    except:
        logger.error('Mandatory config "api_key" is not set!')
        sys.exit(1)
    try:
        config['path']
    except:
        logger.error('Mandatory config "path" is not set!')
        sys.exit(1)
    try:
        config['from_email']
    except:
        logger.error('Mandatory config "from_email" is not set!')
        sys.exit(1)
    try:
        config['mail_subject']
    except:
        logger.error('Mandatory config "mail_subject" is not set!')
        sys.exit(1)
    try:
        config['mail_body']
    except:
        logger.error('Mandatory config "mail_body" is not set!')
        sys.exit(1)
    try:
        config['col_mapping']['first_name']
        config['col_mapping']['last_name']
        config['col_mapping']['email']
        config['col_mapping']['expiry_date']
    except:
        logger.error(
            'One of the mandatory configs within the config "col_mapping" is'
            + ' not set: "first_name", "last_name", "email" and/or'
            + ' "expiry_date"!')
        sys.exit(1)

def is_number(s):
    """
    Check if numeric (incl. floats)
    """

    try:
        float(s)
        return True
    except ValueError:
        return False
