import logging

class Logger:
    def __init__(self,name:str):
        # logging configuration
        self.logger = logging.getLogger(name=name)
        self.logger.setLevel('DEBUG')

        console_handler = logging.StreamHandler()
        console_handler.setLevel('DEBUG')

        file_handler = logging.FileHandler(f'{name}.log')
        file_handler.setLevel('ERROR')

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)