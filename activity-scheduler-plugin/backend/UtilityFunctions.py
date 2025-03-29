import os
import shutil

def email_decorator(func):
    """
    A decorator to handle common email sending setup and error handling.    
    It retrieves email credentials from environment variables, sets up the SMTP server,
    and sends the email. It also includes error handling for common email-related issues.

    Requires environment variables:
        SENDER_EMAIL: Email account for sending
        SENDER_PASSWORD: App password for email account
    """
    import os
    import smtplib    
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        sender_email = os.environ.get('SENDER_EMAIL')
        sender_password = os.environ.get('SENDER_PASSWORD')

        if not all([sender_email, sender_password]):
            raise ValueError("Missing email credentials in environment variables")

        try:
            msg = func(*args, **kwargs)  # Execute the decorated function to get the EmailMessage object
            msg['From'] = sender_email  # Ensure 'From' is set here
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            return True
        except smtplib.SMTPAuthenticationError:
            print("Authentication failed. Check your email credentials.")
            return False
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    return wrapper


def get_files_in_folder(root_dir):    
    """Recursively scan a folder and return list of files with full paths
    Args:
        root_dir - Directory to scan
    Reutnrs:
        List of file names with absolute path
    """
    file_list = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            file_list.append(full_path)
    return file_list

def get_file_types(file_list):    
    """Return dictionary mapping filenames to their file extensions.
    Args:
        List of file names with absolute path
    Returns:
        Dictionary with file name as key and file type as value    
    """
    type_dict = {}
    for file_path in file_list:
        # Split the file extension from the path
        _, ext = os.path.splitext(file_path)
        # Remove leading dot and convert to lowercase for consistency
        clean_ext = ext.lower().lstrip('.') if ext else 'no_extension'
        type_dict[file_path] = clean_ext
    return type_dict

def organize_files(type_dict):
    """Organize files into folders based on their type in their respective directories.
    Args:
        Dictionary with file name as key and file type as value      
    """
    
    for file_path, file_type in type_dict.items():
        # Get parent directory and filename
        parent_dir = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        
        # Create target directory name (pluralize for readability)
        target_dir_name = f"{file_type}s"  # Example: 'pdf' becomes 'pdfs'
        target_dir = os.path.join(parent_dir, target_dir_name)
        
        # Create target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Construct full target path
        target_path = os.path.join(target_dir, filename)
        
        # Only move if source and target paths are different
        if file_path != target_path:
            try:
                shutil.move(file_path, target_path)
                print(f"Moved: {filename} -> {target_dir_name}/")
            except Exception as e:
                print(f"Error moving {filename}: {str(e)}")

def zip_folder(folder_path):
    """Create a zip archive of the specified folder in its parent directory.
    Args:
        Folder name along with the absolute path    
    """
    import os
    import shutil
    try:
        parent_dir = os.path.dirname(folder_path)
        folder_name = os.path.basename(folder_path)
        # Check if the path is a file or a folder
        if os.path.isfile(folder_path):
            # If it's a file, create a zip archive of the file
            shutil.make_archive(os.path.splitext(folder_path)[0], 'zip', root_dir=parent_dir, base_dir=os.path.basename(parent_dir))
            print(f"Created {folder_name}.zip in {parent_dir}")
        else:
            # If it's a folder, create a zip archive of the folder
            shutil.make_archive(folder_path, 'zip', parent_dir, folder_name)
            print(f"Created {folder_name}.zip in {parent_dir}")
        return True
    except FileExistsError as e:
        print(f"FileExistsError: {str(e)}")
        return False
    except Exception as e:
        print(f"Error zipping folder: {str(e)}")
        return False
    

@email_decorator
def send_reminder_email(email_id, task):
    """Send a reminder email for a task     
    Args:
        email_id: this is a positional argument. Recipient email address should be passed here
        task: this is a positional argument, indicates the task description to include in the reminder.    
    """
    from email.message import EmailMessage
    # Create email message
    msg = EmailMessage()
    msg['Subject'] = 'Task Reminder'
    msg['To'] = email_id
    msg.set_content(f'Reminder for your task:\n\n{task}')
    
    return msg

@email_decorator
def add_calendar_invite(task, date, email):
    """Create and send a calendar invite for a task on specified date/time to given email.    
    Args:
        task: Task description for the calendar event
        date: datetime object for the event start time
        email: Recipient email address    
    """
    import smtplib
    import os
    from email.message import EmailMessage
    import datetime
    import uuid

    sender_email = os.environ.get('SENDER_EMAIL')
           
    # Generate unique ID for the event
    uid = uuid.uuid4()
    
    # Calculate end time (1 hour after start)
    start_time = date
    end_time = start_time + datetime.timedelta(hours=1)
    
    # Format times in UTC
    dtstamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dtstart = start_time.astimezone(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dtend = end_time.astimezone(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    # Create ICS content
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Task Manager//Calendar Invite//EN
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{task}
ORGANIZER:mailto:{sender_email}
ATTENDEE:mailto:{email}
END:VEVENT
END:VCALENDAR
""".replace('\n', '\r\n')  # Convert to CRLF line endings
    
    # Create email message
    msg = EmailMessage()
    msg['Subject'] = f'Calendar Invite: {task}'
    msg['To'] = email
    msg.set_content('Please find the calendar invite attached.')    
    # Attach ICS file
    msg.add_attachment(ics_content, subtype='calendar', filename='invite.ics')    
    return msg

import yfinance as yf
import time
import os
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from apscheduler.schedulers.background import BackgroundScheduler

def get_stock_price(stock_name):
    """Gets the stock price of a given stock   
    Args:
        stock_name: Name of stock as listed in stock market   
    """
    stock = yf.Ticker(stock_name)
    data = stock.history(period='1d')
    return data['Close'].iloc[-1]

@email_decorator
def send_stock_email(email, stock_name):
    """sends the price of the given stock to the given email.    
    Args:
        stock_name: Name of stock as listed in stock market   
        email: Recipient email address      
    """
    price = get_stock_price(stock_name)
        
    msg = EmailMessage()
    msg['Subject'] = f'NVIDIA Stock Price Update: ${price:.2f}'
    msg['To'] = email
    msg.set_content(f'Current NVIDIA stock price: ${price:.2f}')
    return msg
    

def schedule_daily_stock_email(email, stock_name="NVDA"):
    """Schedules and sends the price of the given stock to the given email everyday at 5 pm.   
    Args:
        stock_name: Name of stock as listed in stock market, Defaut value being Nvidia - NVDA 
        email: Recipient email address      
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_stock_email,
        'cron',
        hour=17,
        minute=0,
        args=[email, stock_name]
    )
    scheduler.start()
