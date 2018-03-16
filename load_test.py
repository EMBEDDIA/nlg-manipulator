from molotov import scenario

@scenario(100)
async def scenario_one(session):
    async with session.get('http://localhost:8080/random') as resp:
        assert resp.status == 200, resp.status
