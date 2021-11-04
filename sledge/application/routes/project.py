#project.py


import orjson as json
from unsync import unsync 

from os import access, getlogin, name

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
from application.routes.employee import Employee

class Project:
    _id:str = None
    name:str = None
    meta_data:dict = {}
    index:set = set()
    project:dict = {}
    projects:list= []


    def __init__(self, data:dict=None) -> None:
        try:
            from aspiredb.core.encriptor import GenerateId
            self.keygen = GenerateId()
            if data:
                self.mount(data)
            else:
                self._id = self.keygen.name_id("S", "T")
        except ImportError as e:
            print(str(e))
        finally:
            del(GenerateId)
            del(data)
            self.loadprojects()

    
    def mount(self, data:dict=None) -> None:        
        self.data = DictClass(data)
        self._id = self.keygen.name_id(self.data.name, self.data.name[:-1])
        self.data._id = self._id
        self.data.meta_data = self.metadata
        

    async def update_index(self, data:str) -> None:
        '''  Expects a unique id string ex. JD33766'''        
        self.index.add(data) 


    @property 
    def list_index(self) -> list:
        ''' Converts set index to readable list'''
        return [item for item in self.index]


    @property
    def worker(self):
        return Employee()


    async def process_workers(self, index:list=None) -> dict:
        try:
            employees = []
            if len(index) > 0:
                for eid in index: 
                    worker = await self.worker.get_employee(eid)
                    employees.append(worker)                
              
                return {"employees": employees} 
            else: return {"employees": []}                     
        except:
            pass
        finally: 
            del(employees) 


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
        res = json.loads(await self.con.create_database(dbname='project', access="public"))
        return res

    
    async def createproject(self, data:dict=None):
        '''Creates a new project '''
        self.mount(data)
        payload = self.data.to_dict()
        print(payload)
        project = json.loads( await self.con.create_document(database='project', data=payload))
        return project


    @unsync
    async def loadprojects(self):
        self.projects = json.loads(await self.con.get_documents(dbname='project'))


    def projectCount(self):
        ''''''

    
    async def getTask(self, task_id:str=None):
        ''''Retreives a task from the project. Requires the assigned task id '''
        try:            
            ends = task_id.split('-')
                
            def findTask(task):
                return task['_id'] == task_id
        
            project = json.loads( await self.con.get_document(dbname='project', doc_id=ends[0]))                 
            task = list(filter( findTask, project.get('tasks') ))
            return task[0]
        except Exception as e:
            return {'error': str(e)}


    async def getEmployeeTasks(self, pe_id:str=None):
        ''''Retreives a batch of tasks assigned to the employee  from the project. 
        Requires the project id and the employee id'''
        try:            
            ends = pe_id.split('-')
                
            def findTasks(task):
                return task['assignedto'] == ends[1]
        
            project = json.loads( await self.con.get_document(dbname='project', doc_id=ends[0]))                 
            tasks = list(filter( findTasks, project.get('tasks') ))
            return tasks

        except Exception as e:            
            return {'error': str(e)}



pro = Project()

#................... API's .................................

async def createdb(request):
    return JSONResponse(await pro.createdb())

async def count(request):
    ''''''
    return JSONResponse( len(pro.projects))   


async def getAll(request):
    '''GET operation yeilds a list of all documents'''    
    projects = json.loads(await pro.con.get_documents(dbname='project'))
    return JSONResponse(projects)


async def get(request):    
    '''GET operation yeilds a documents'''    
    id = request.path_params['id']
    project = json.loads( await pro.con.get_document(dbname='project', doc_id=id))
    workers = await pro.process_workers(project.get('employees')) 
    project['process'] = workers 
    return JSONResponse(project)


async def getTasks(request):    
    '''GET operation yeilds a documents'''    
    id = request.path_params['id']
    project = json.loads( await pro.con.get_document(dbname='project', doc_id=id))        
    return JSONResponse(project.get('tasks'))


async def getTask(request):    
    '''GET operation yeilds a document'''    
    return JSONResponse( await pro.getTask(task_id=request.path_params['pt']) )

async def getEmployeeTasks(request):    
    '''GET operation yeilds batch of documents'''    
    return JSONResponse( await pro.getEmployeeTasks(pe_id=request.path_params['pe']) )


async def createProject(request):
    '''Creates a new project'''
    data = await request.json()
    return JSONResponse( await pro.createproject(data=data))


async def updateProject(request):
    '''Update project'''
    id = request.path_params['id']
    data = await request.json()
    result = json.loads( await pro.con.update_document(dbname='project', doc_id=id, data=data))
    return JSONResponse(result)

#.............. HTML ..........................


async def assignWorkerTask(request):
        '''GET operation yeilds a single document by request id'''        
        taskid = request.path_params['taskid']
        #project = json.loads( await pro.con.get_document(dbname='project', doc_id=id))
        #workers = await pro.process_workers(project.get('employees'))      
        print( taskid)#, project)         
        return JSONResponse({'username': getlogin()})#, 'id':id,'project': project})
   


router:list= [
    Route('/', endpoint=getAll),
    Route('/get/{id}', endpoint=get),  
    Route('/task/{pt}', endpoint=getTask, methods=['GET']),
    Route('/employeetasks/{pe}', endpoint=getEmployeeTasks, methods=['GET']),   
    Route('/worker_task/{taskid}', endpoint=assignWorkerTask),   
    Route('/create', endpoint=createProject,  methods=['POST']),
    Route('/createdb', endpoint=createdb),
    Route('/count', endpoint=count ),
    Route('/{id}/tasks/', endpoint=getTasks),
    Route('/update/{id}', endpoint=updateProject, methods=['POST']),
    
]


project = Aspiration(
    routes=router,
    debug=True
)