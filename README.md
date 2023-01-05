# Alma (ExLibris): Notify expiring users

This Python script is intended to work with Alma (ExLibris) to notify users that are about to expire by e-mail.

## Prerequisites

- (Linux) Server - not tested on Windows!
- Python 3.6 or higher
- Mail Transfer Agent (e. g. Postfix)
  > **Warning**
  > Make sure your server is configured properly for sending e-mails. Otherwise, the notifications could be treated as spam.

## Installation

1. Clone the repository

   ```bash
   git clone https://... $path_to_repo
   ```

1. Change into the directory of the repository

   ```bash
   cd $path_to_repo
   ```

1. Create a virtual environment

   ```bash
   python -m venv .venv
   ```

1. Activate the virtual environment

   ```bash
   source .venv/bin/activate
   ```

1. Upgrade `pip`

   ```bash
   python -m pip install --upgrade pip
   ```

1. Install the python dependencies

   ```bash
   python -m pip install -r requirements.txt
   ```

## Configuration

1. Copy the `config.example.py` to `config.py`
1. Adjust all configs to your needs (see the comments in the config file)

## Testing

1. In the config file, set your test e-mail address to the config `to_email_test`. Every e-mail that would normaly be sent to a user will now be sent to this e-mail address.

1. Run the script and check if everything works as expected:
   - Within the path of the repository, activate the virtual environment

      ```bash
      source .venv/bin/activate
      ```

   - Run the script and check your e-mails.

     ```bash
     python3 $path_to_repo/notify-expiring-users.py
     ```

1. When testing is finished, comment out the `to_email_test` config or set it to None. Then, the e-mails will be sent to the real users.

## Run the script once daily

1. Use a cronjob that runs the script once daily.
   > **Warning**
   > If the cron job runs multiple time per day, the users that are about to expire will receive multiple e-mails. Therefore it is recommended to run the job only once a day.

1. Cronjobs can be run for a specific user or from the systems `/etc/crontab` file. Choose which way is the most appropriate for you.

1. A cronjob in `/etc/crontab` that runs the script every day at 06:00 o'clock could look like this:

   ```cron
   0 6 * * * root $path_to_repo/.venv/bin/python $path_to_repo/notify-expiring-users.py
   ```

   > **Warning**
   > Make sure that you use the python from your virtual environment!
