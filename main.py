from fastapi import FastAPI, Query
from typing import Annotated
from Connect_to_MongoDB import main

app = FastAPI()


@app.get('/team_info')
async def team_info(team_name: str, decrease: Annotated[bool, Query()] = False):
    team_name = team_name.title()
    info = await main(team_name, decrease)
    return info
