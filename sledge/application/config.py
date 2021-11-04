import os


from asyncio.locks import Semaphore
try:

    from application.bin.utils.ssl import scrp
except ImportError:
    from sledge.application.bin.utils.ssl import scrp

from aspire.core.reactor import ( 
    JinjaTemplates,
    PlainTextResponse, 
    Route, 
    Mount,
    StaticFiles)



class Config:
    ''''''
    #.......... Directories ..................

    BASE_PATH = os.path.abspath(os.getcwd())
    STATIC_PATH = os.path.join(BASE_PATH, 'static')
    TEMPLATES_PATH = os.path.join(BASE_PATH, 'templates')
    BIN_PATH = os.path.join(BASE_PATH, 'bin')
    DLL_PATH = os.path.join(BIN_PATH, 'dlls')
    UTIL_PATH = os.path.join(BIN_PATH, 'utils')
    SSL_PATH = os.path.join(BASE_PATH, '.ssl')
    FILES = os.listdir(STATIC_PATH)

    #............... Network Config ..........
    PORT = 9456
    HOST = '0.0.0.0'

    #............... secutity ................

    SECRET_KEY = scrp.syskey

    #.............. Async Management .........
    
    SEMAPHORE = Semaphore(200)

    #............. Templates ............

    templates = JinjaTemplates(directory=TEMPLATES_PATH) 




config = Config()