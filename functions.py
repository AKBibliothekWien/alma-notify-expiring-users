import sys
import logging
import datetime
import smtplib
from email.message import EmailMessage
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
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)-5s - %(module)-20s - Line %(lineno)04d: %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
    #formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)-5s: %(message)s', datefmt='%d.%m.%Y %H:%M:%S')
    # "Logging to file" handler
    if log_file is not None:
        rotating_file_handler = RotatingFileHandler(log_file, maxBytes=500000, backupCount=5)
        rotating_file_handler.setFormatter(formatter)
        logger.addHandler(rotating_file_handler)
    # "Logging to console" handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def send_mail(first_name: str, last_name: str, expiry_date: datetime.date, date_format: str, to_mail: str, from_mail: str, mail_subject:str, mail_body: str):
    """
    Send an HTML email
    """    
    first_name_clean = str(first_name if first_name is not None and first_name.strip() != '' else '')
    last_name_clean = str(last_name if last_name is not None and last_name.strip() != '' else '')
    expiry_date_formatted = expiry_date.strftime(date_format)
    mail_subject_formatted = mail_subject.format(first_name=first_name_clean, last_name=last_name_clean, expiry_date=expiry_date_formatted)
    mail_body_formatted = mail_body.format(first_name=first_name_clean, last_name=last_name_clean, expiry_date=expiry_date_formatted)

    # Remove two consecutive spaces from mail subject and mail body (e. g. when first_name is empty)
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
