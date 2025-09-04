from fastapi import Request, FastAPI, HTTPException
import shutil
from ncoreparser import Client, SearchParamWhere, SearchParamType, ParamSort, ParamSeq
from fastapi.middleware.cors import CORSMiddleware
import psutil
from ncoreparser.torrent import Torrent
from pydantic import BaseModel

class Data(BaseModel):
  id: str
  download: str
  title: str
  leech: int
  seed: int
  title: str
  type: str
  date: str

app = FastAPI()
app.client = None
app.username = "minya97"
app.password = "kD-AsLQuSPeOuQBxsqIR"

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def ensure_logged_in():
    """Ensure client is logged in, re-login if session expired"""
    try:
        if app.client is None:
            app.client = Client()
            app.client.login(app.username, app.password)
        else:
            # Test if session is still valid by making a small request
            app.client.get_recommended(type=SearchParamType.HD_HUN, number=1)
    except Exception as e:
        # Session expired or other error, re-login
        try:
            app.client = Client()
            app.client.login(app.username, app.password)
        except Exception as login_error:
            raise HTTPException(status_code=500, detail=f"Login failed: {str(login_error)}")

@app.on_event("startup")
async def startup_event():
    ensure_logged_in()

@app.get("/api/test")
async def test():
  return {"message":dir(SearchParamType)}

@app.get("/api/login")
async def login():
  ensure_logged_in()
  return {"message":"Login successful"}

@app.get("/api/logout")
async def logout():
  if app.client:
    app.client.logout()
    app.client = None
  return {"message":"Logout"}

@app.get("/api/torrents")
async def root(pattern,type: SearchParamType = SearchParamType.HD_HUN):
  ensure_logged_in()
  torrents = app.client.search(
            pattern=pattern,
            type=type,
            sort_by=ParamSort.SEEDERS,
            sort_order=ParamSeq.DECREASING
        )
  return torrents

@app.post("/api/torrents/download")
async def download_torrent(request: Request):
    ensure_logged_in()
    torrent_data = await request.json()
    downloadable_torrent = Torrent(**torrent_data)
    app.client.download(downloadable_torrent, "/torrents")
    return {"message": "Downloaded"}

@app.get("/api/disk/free")
async def get_free_space():
  obj_Disk = psutil.disk_usage('/')
  return {"data":obj_Disk.free / (1024.0 ** 3)}

@app.get("/api/torrents/recommended")
async def get_all():
  ensure_logged_in()
  torrents = app.client.get_recommended(type=SearchParamType.HD_HUN)
  for torrent in torrents:
      print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

  return {"torrents": torrents}