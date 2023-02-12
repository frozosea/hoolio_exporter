from loguru import logger
from builder import Builder

if __name__ == '__main__':
    logger.info("START CONFIGURE PROJECT")
    transport = Builder().configure()
    logger.info("BUILT SUCCESS")
    transport.run()
