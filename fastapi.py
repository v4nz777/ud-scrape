from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main import App as ScraperApp
from fastapi.responses import StreamingResponse
import json
import asyncio

app = FastAPI()


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scrape/{provider}")
async def getDatafrom(provider:str) -> StreamingResponse:
    providers = ['realdiscount','discudemy','udemyfreebies']
    if provider not in providers: 
        return {"message":"Error: provider not valid."}
    else:
        scraper_script = ScraperApp()

        async def data_generator():
            gen = scraper_script.run(provider)
            async for item in await asyncio.to_thread(list, gen):
                yield item
        return StreamingResponse(data_generator())

# scraper_script = ScraperApp()
# for i in scraper_script.run('udemyfreebies'):
#     print('streaming',i)