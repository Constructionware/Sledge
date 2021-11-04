#employee.py

import orjson as json
from os import access, getlogin

#from aspiredb.core.encriptor import GenerateId

from aspiredb.database import Controller

from dictclass import DictClass

from asyncio.locks import Semaphore

semaphore = Semaphore(200)

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

class Employee:

    _id:str = None
    meta_data:dict = {}
    index:set = set()
    employee:dict = {}
    employees:list= []
    router:list= []

    def __init__(self, data:dict=None) -> None:
        try:
            from aspiredb.core.encriptor import GenerateId
            self.keygen = GenerateId()
            if data:
                self.data = DictClass(data)
                self._id = self.keygen.name_id(self.data.fname, self.data.lname)
                self.data["_id"] = self._id
            else:
                self._id = self.keygen.name_id("S", "E")
        except ImportError as e:
            print(str(e))
        finally:
            self.router = self.routerer #.append(Route('/', endpoint=self.indexPage))
            del(GenerateId)
            del(data)
        


    def mount(self, data:dict=None) -> None:        
        if data:
            self.data = DictClass(data)
            self._id = self.keygen.name_id(self.data.fname, self.data.lname)
            self.data._id = self._id
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

    
    async def createdb(self):
        ''' Create a New Public database for this module'''
        res = json.loads(await self.con.create_database(dbname='employee', access="public"))
        return res

    @property
    async def get_employees(self) -> list:    
        '''GET operation yeilds a list of all documents'''    
        result = json.loads(await self.con.get_documents(dbname='employee'))
        return result

    async def get_employee(self, id) -> dict:
        '''GET operation yeilds a single document by request id'''
        result = json.loads( await self.con.get_document(dbname='employee', doc_id=id))
        return result

    async def create(self, data):
        await semaphore.acquire()
        try:
            self.mount(data)
            processed = self.data.to_dict()
            self.meta_data['created'] = self.con.slave.time_stamp
            self.meta_data['author'] = getlogin()
            processed['meta_data'] = self.meta_data        
            result = json.loads(await self.con.create_document(database='employee', data=processed))
            return result
        except Exception as e:
            return {"status": str(e)}
        finally:
            await self.load_index
            semaphore.release()

    async def update(self, id,  data):
        await self.con.update_document()
        result = json.loads(await self.con.update_document(dbname='employee', doc_id=id,  data=data))
        return result

    async def delete(self, id):
        #result = json.loads(await self.con.delete_document(database='employee', data=data))
        result = {"status": "Sorry Deletions are not allowed at this time"}
        return result

    async def clone(self, id, clone_id):
        result = json.loads( await self.con.clone_doc(dbname='employee', doc_id=id, clone_id=clone_id))
        return result

    @property
    async def get_name_index(self) -> list:        
        employees = await self.get_employees        
        def filter(data):
            return {
                "id": data['_id'],
                "name": f"{data['fname']} {data['lname']}",
                "alias": data.get('alias'),
                "occupation": data['occupation'],
                "imgurl": data['imgurl'],
                "contact": data.get('contact')
                }
        self.name_index = list(map(filter, employees))
        del(employees) # cleanup        
        return self.name_index        

    @property
    async def get_nextofkin(self) -> list:        
        employees = await self.get_employees        
        def filter(data):
            return {
                    "id": data['_id'],
                    "name": f"{data['fname']} {data['lname']}",
                    "nok": data.get('nok')
                    }
        nok_index = list(map(filter, employees))
        del(employees) # cleanup
        return nok_index

    @property
    async def get_occupations(self) -> list:        
        employees = await self.get_employees        
        def filter(data):
            return {
                "id": data['_id'],
                "name": f"{data['fname']} {data['lname']}",
                "occupation": data.get('occupation')
                }
        o_index = list(map(filter, employees))
        del(employees) # cleanup
        return o_index   
    
    # LOADS 
    @property   
    async def load_index(self):
        try:           
            for item in await self.get_name_index:
                self.index.add(item['id'])
        except Exception as e:
            print(e) # Log
   
    # VALIDATION
    @property
    async def __check_exist(self):
        if self.data._id in self.index:
            return True
        return False
    #............ HTTP .......................

    async def indexPage(self, request):
        employees = await self.get_employees
           
        return config.templates.TemplateResponse('employee/index.html', {'request': request, 'username': getlogin(), 'employees': employees})


    @property
    def routerer(self):
        ''''''
        return [
            Route('/', endpoint=self.indexPage),
           
        ]

 
employee = Employee()

async def index(request):            
        return JSONResponse( await employee.get_employees  )


async def getOne(request):
    ''' Handles Request GET for app Main Client'''
    await semaphore.acquire()
    try:       
        return JSONResponse(await employee.get_employee(request.path_params['id'] ))
    except Exception as e:
        return {'error': str(e)}
    finally:
        semaphore.release()


async def createOne(request):
    ''' Handles POST requests '''  
    return JSONResponse(await employee.create(await request.json()))

async def update_index(request):
    await employee.load_index
    return JSONResponse(employee.list_index)

async def update(request):  
    return JSONResponse(
        await employee.update(id=request.path_params['id'], 
        data=await request.json())
    )

async def createdb(request):
    return JSONResponse(await employee.createdb())


async def name_index(request):
        return JSONResponse( await employee.get_name_index )  



router = [
    Route('/', endpoint=index, methods=['GET']),
    Route('/get/{id}', endpoint=getOne),    
    Route('/create', endpoint=createOne, methods=['POST']),
    Route('/createdb', endpoint=createdb),
    Route('/update_index', endpoint=update_index), 
    Route('/employees_index', endpoint=name_index, methods=['GET']),  
    Route('/update/{id}', endpoint=update, methods=['POST']),
           
           
]   

esrv = Aspiration(
    routes=router,
    debug=True
)