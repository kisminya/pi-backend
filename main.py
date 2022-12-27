from fastapi import Request, FastAPI
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

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/test")
async def login():
  return {"message":"Test"}

@app.get("/api/login")
async def login():
  app.client = Client()
  app.client.login("", "")
  return {"message":"Login"}

@app.get("/api/logout")
async def logout():
  app.client.logout()
  return {"message":"Logout"}

@app.get("/api/torrents")
async def root(type, pattern):
  torrents = []
  print(type,pattern);
  torrent = app.client.search(pattern=pattern, type=SearchParamType[type], number=1,
  sort_by=ParamSort.SEEDERS, sort_order=ParamSeq.DECREASING)[0]
  return torrent

@app.post("/api/torrents/download")
async def download_torrent(request: Request):
    torrent_data = await request.json()
    downloadable_torrent = Torrent(**torrent_data)
    app.client.download(downloadable_torrent, "torrents")
    return {"message": "Downloaded"}

@app.get("/api/disk/free")
async def get_free_space():
  obj_Disk = psutil.disk_usage('/')
  return {"data":obj_Disk.free / (1024.0 ** 3)}

@app.get("/api/torrents/recommended")
async def get_all():
  torrents = app.client.get_recommended(type=SearchParamType.HD_HUN)
  for torrent in torrents:
      print(torrent['title'], torrent['type'], torrent['size'], torrent['id'])

  return {torrents}

