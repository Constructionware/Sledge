#task

import orjson as json
from unsync import unsync 

from os import access, getlogin, name

#from aspiredb.core.encriptor import GenerateId

from aspiredb.database import Controller

from dictclass import DictClass

from asyncio.locks import Semaphore


from aspire.core.app_stack import Aspiration
from aspire.core.security_service import CORSMiddleware
from aspire.core.reactor import ( 
    JSONResponse,
    JinjaTemplates,
    PlainTextResponse, 
    Route, 
    Mount,
    StaticFiles, 
    )


from application.config import config
from application.routes.employee import Employee


semaphore = config.SEMAPHORE

class Task:
    name:str = "task"
    _id:str = None
    meta_data:dict = {}
    index:set = set()
    task:dict = {}
    tasks:list= []

    def __init__(self, data:dict=None) -> None:
        try:
            from aspiredb.core.encriptor import GenerateId
            self.keygen = GenerateId()
            if data:
                self.data = DictClass(data)
                self._id = self.keygen.name_id(self.data.title, self.data.title[:-1])
                self.data["_id"] = self._id
            else:
                self._id = self.keygen.name_id("S", "T")
        except ImportError as e:
            print(str(e))
        finally:
            del(GenerateId)
            del(data)
            self.loadTasks()

    
    def mount(self, data:dict=None) -> None:        
        if data:
            self.data = DictClass(data)
            self._id = self.keygen.name_id(self.data.title, self.data.title[:-1])
            self.data._id = self._id
            self.data.meta_data = self.metadata
        else:
            pass

    async def update_index(self, data:str) -> None:
        '''  Expects a unique id string ex. JD33766'''        
        self.index.add(data) 


    @property 
    def list_index(self) -> list:
        ''' Converts set index to readable list'''
        return [item for item in self.index]


    @property
    def con(self):
        ''' Aspire database controller '''
        return Controller()

    @property
    def handle(self):
        ''' data end points '''
        return self.con.handle

    @property
    def metadata(self):
        self.meta_data['created'] = self.con.slave.time_stamp
        self.meta_data['author'] = getlogin()
        return self.meta_data


    
    async def createdb(self):
        ''' Create a New Public database for this module'''
        res = json.loads(await self.con.create_database(dbname='task', access="public"))
        return res

    
    async def createTask(self, data:dict=None):
        '''Creates a new Task '''
        self.mount(data)
        payload = self.data.to_dict()
        print(payload)
        task = json.loads( await self.con.create_document(database='task', data=payload))
        return task

    @unsync
    async def loadTasks(self):
        self.tasks = json.loads(await self.con.get_documents(dbname='task'))

task = Task()

#................... API's .................................
async def createdb(request):
    return JSONResponse(await task.createdb())

async def getAll(request):    
    '''GET operation yeilds a list of all documents'''    
    tasks = json.loads(await task.con.get_documents(dbname='task'))
    return JSONResponse(tasks)


async def get(request) -> dict:
    '''GET operation yeilds a single document by request id'''
    id = request.path_params.get('id', None)
    data = json.loads( await task.con.get_document(dbname='task', doc_id=id))
    return JSONResponse(data)


async def createOne(request):
    ''' Handles POST requests ''' 
    data = await request.json()  
    result = await task.createTask(data=data)
    return JSONResponse( result )


async def update(request):
    '''Update project'''
    id = request.path_params['id']
    data = await request.json()
    result = json.loads( await task.con.update_document(dbname='task', doc_id=id, data=dict(data)))    
    
    tasks = json.loads(await task.con.get_documents(dbname='task'))    
    return config.templates.TemplateResponse('task/task.html', {'request': request, 'username': getlogin(), 'task': result, 'tasks': tasks})
 

#................. HTML ............................

routes = [
    Route('/', endpoint=getAll),
    Route('/get/{id}', endpoint=get),
    Route('/create', endpoint=createOne, methods=['POST']),
    Route('/createdb', endpoint=createdb),
    Route('/update/{id}', endpoint=update, methods=['POST']),
   
]


taskr = Aspiration(
    routes=routes,
    debug=True
)