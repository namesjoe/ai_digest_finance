import logging

def get_logger(name):
    """
    Создаёт и возвращает настроенный логгер.

    Args:
        name (str): Имя логгера

    Returns:
        logging.Logger: Настроенный логгер.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    logger.addHandler(ch)
    return logger

