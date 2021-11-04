#server.py
from aspire.core.security_service import CORSMiddleware, GenerateId
from aspire.core.app_stack import Aspiration
from aspire.core.reactor import (
    JinjaTemplates,
    PlainTextResponse,
    JSONResponse,
    Route,
    Mount,
    StaticFiles,
)


from application.config import config
from application.routes.employee import esrv
from application.routes.task import taskr
from application.routes.project import project


async def homePage(request):
    return JSONResponse({'message': 'Welcome! This is the Sledge Server.'})

routes = [ 
    Route('/', endpoint=homePage),
    Mount('/employee', esrv),
    Mount('/task', taskr),
    Mount('/project', project),
    Mount('/static', StaticFiles(directory=config.STATIC_PATH)),
]

app = Aspiration(
    routes=routes,
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
    allow_origin_regex=None,
    expose_headers=[ 
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Cedentials",
        "Access-Control-Allow-Expose-Headers",
    ],
    max_age=3600,
    
)


def main():
    print("Happy Sledging....")
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5777)
    