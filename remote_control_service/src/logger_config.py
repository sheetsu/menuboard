import logging
from logging.handlers import RotatingFileHandler

log_file = "/home/pi/menuboard/remote_control_service/logs/app.log"

logger = logging.getLogger("RotatingLog")

logger.setLevel(logging.INFO) #Set logging.DEBUG if you want to debug something on prod env

handler = RotatingFileHandler(
    log_file,
    maxBytes=20 * 1024 * 1024,  
    backupCount=1            
)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)