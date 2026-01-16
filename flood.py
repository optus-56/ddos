import asyncio
import aiohttp
import time
import random

async def hit_endpoint(session, url, method='GET', payload=None, headers=None):
	try:
		if method == 'POST':
			async with session.post(url, json=payload, headers=headers) as resp:
				await resp.text()
		else:
			async with session.get(url) as resp:
				await resp.text()
	except:
		pass
		
async def flood(urls, concurrency=500, duration=60, post_data=None):
	connector = aiohttp.TCPConnector(limit=concurrency, limit_per_host=100)
	async with aiohttp.ClientSession(connector=connector) as session:
		start = time.time()
		tasks = []
		while time.time() - start < duration:
			url = random.choice(urls)
			tasks.append(hit_endpoint(session, url, payload=post_data))
			if len(tasks) >= concurrency:
				await asyncio.gather(*tasks)
				tasks = []
		if tasks:
			await asyncio.gather(*tasks)

API_ENDPOINTS = [
	"http://localhost:8000/analysis/voltage"
]

POST_PAYLOAD = {"username": "test", "password": "test"}

asyncio.run(flood(API_ENDPOINTS, concurrency = 1000, duration=300, post_data=POST_PAYLOAD))