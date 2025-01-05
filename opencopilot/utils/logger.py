import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from termcolor import colored
import json
import zipfile
from datetime import datetime
import glob

COLOR_BLACK = "black"
COLOR_RED = "red"
COLOR_GREEN = "green"
COLOR_YELLOW = "yellow"
COLOR_BLUE = "blue"
COLOR_MAGENTA = "magenta"
COLOR_CYAN = "cyan"
COLOR_WHITE = "white"
COLOR_GREY = "grey"

all_colors = [COLOR_BLACK, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE, COLOR_MAGENTA, COLOR_CYAN, COLOR_WHITE, COLOR_GREY]

class LogFileFullException(Exception):
    pass

# Decorator to handle exceptions in logging methods
def handle_logging_exceptions(func):
    """
    Decorator to handle exceptions in logging methods.
    Detects if the log file is full and raises a custom exception.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OSError as e:
            # Detect if the error is related to disk or file being full
            if e.errno == 28:  # Error code 28: No space left on device
                raise LogFileFullException("Log file is full or disk space is exhausted.")
            else:
                raise  # Re-raise other exceptions
        except Exception as e:
            # Handle other generic exceptions if necessary
            print(f"Unexpected logging error: {e}")
            return None  # Prevent further propagation of the exception
    return wrapper


class ZipRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.rotator = self.rotate_file
        self.max_zips = backupCount

    @handle_logging_exceptions
    def rotate_file(self, source, dest):
        if os.path.exists(source):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_path = os.path.splitext(dest)[0]
            zip_filename = f"{base_path}_{timestamp}.zip"
            
            try:
                with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(source, os.path.basename(source))
                
                # After successful compression, delete the original log file
                os.remove(source)
                
                # Check and maintain the zip file limit
                self.maintain_zip_limit(base_path)
                
            except Exception as e:
                print(f"Error zipping log file: {e}")
    @handle_logging_exceptions
    def maintain_zip_limit(self, base_path):
        # Get all zip files with the base path
        zip_pattern = f"{base_path}_*.zip"
        zip_files = glob.glob(zip_pattern)
        
        # Sort zip files by modification time (oldest first)
        zip_files.sort(key=os.path.getmtime)
        
        # Remove oldest files if we exceed the limit
        while len(zip_files) > self.max_zips:
            oldest_file = zip_files.pop(0)
            try:
                os.remove(oldest_file)
                print(f"Deleted old log zip: {oldest_file}")
            except Exception as e:
                print(f"Error deleting old log zip {oldest_file}: {e}")

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename("%s.%d" % (self.baseFilename, i))
                dfn = self.rotation_filename("%s.%d" % (self.baseFilename, i + 1))
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate_file(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()


class StreamToLogger(object):
    def __init__(self, logger, log_level, original_stream):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''
        self.original_stream = original_stream
    @handle_logging_exceptions
    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
        self.original_stream.write(buf)  # Write to the original stream as well

    @handle_logging_exceptions
    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()
        self.original_stream.flush()  # Flush the original stream as well

__internal_logger = None  # Ensure global declaration here

def get_logger():
    global __internal_logger
    if __internal_logger is None:
        __internal_logger = setup_logger()  # Ensure logger is set up
    return __internal_logger

def setup_logger():
    global __internal_logger
    if __internal_logger is not None:
        return __internal_logger
    
    # Read the COPILOT_LOG_LEVEL environment variable
    log_level_str = os.environ.get("COPILOT_LOG_LEVEL", "ERROR")
    log_level = getattr(logging, log_level_str.upper(), logging.ERROR)

    # Set up the logging configuration with a rotating file handler
    logs_path = os.environ.get("COPILOT_LOG_PATH", "")
    log_file = os.path.join(logs_path, 'app.log')

    max_file_size_bytes = 1024 * 1024 * 128  # 128 MB
    backup_count = 30  # Number of backup files to keep

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create the directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a rotating file handler that compresses old log files
    rotating_handler = ZipRotatingFileHandler(log_file, maxBytes=max_file_size_bytes, backupCount=backup_count)
    rotating_handler.setFormatter(formatter)

    # Create a logger and add the rotating file handler
    __internal_logger = logging.getLogger(__name__)
    __internal_logger.addHandler(rotating_handler)
    __internal_logger.setLevel(log_level)

    # Redirect stderr to the logger
    sys.stderr = StreamToLogger(__internal_logger, logging.ERROR, sys.stderr)

    return __internal_logger

def print_colored(message, color):
    if get_logger().isEnabledFor(logging.INFO):  # Always use get_logger() to ensure it's initialized
        print(colored(message, color))

def print_all_colors():
    for color in all_colors:
        print_colored(f"Hello world!: {color}", color)

@handle_logging_exceptions
def info(message):
    print_colored(message, COLOR_GREEN)
    get_logger().info(message)

@handle_logging_exceptions
def warning(message):
    print_colored(message, COLOR_YELLOW)
    get_logger().warning(message)

@handle_logging_exceptions
def trace(message):
    print_colored(message, COLOR_YELLOW)
    get_logger().debug(message)

@handle_logging_exceptions
def error(message):
    print_colored(message, COLOR_RED)
    get_logger().error(message)

@handle_logging_exceptions
def operator_response(message):
    print_colored(message, COLOR_CYAN)
    get_logger().debug(message)

@handle_logging_exceptions
def operator_input(message):
    operator_response(message)

@handle_logging_exceptions
def system_message(message):
    print_colored(message, COLOR_BLUE)
    get_logger().debug(message)

@handle_logging_exceptions
def predefined_message(message):
    print_colored(message, COLOR_MAGENTA)
    get_logger().debug(message)

@handle_logging_exceptions
def print_tasks(tasks_json_array):
    for task in tasks_json_array:
        color = COLOR_YELLOW if task.get("status") == "TODO" else COLOR_GREEN
        task_json = json.dumps(task, indent=2)
        print_colored(task_json, color)
        get_logger().debug(task_json)

def print_gpt_messages(messages):
    for message in messages:
        role = message['role']
        content = message['content']
        operator_response(f"{role}: {content}")
