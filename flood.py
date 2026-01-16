import asyncio
import aiohttp
import time
import random
from datetime import datetime

async def long_running_request(session, url, duration=3600, payload=None, headers=None):
    """Single request that holds connection for full duration (1 hour)"""
    try:
        timeout = aiohttp.ClientTimeout(total=duration + 10)
        method = random.choice(['GET', 'POST']) if payload else 'GET'
        
        if method == 'POST':
            async with session.post(url, json=payload, headers=headers, timeout=timeout) as resp:
                await asyncio.sleep(duration) 
                try:
                    await resp.text()
                except:
                    pass
        else:
            async with session.get(url, headers=headers, timeout=timeout) as resp:
                await asyncio.sleep(duration)
                try:
                    await resp.text()
                except:
                    pass
        return True
    except:
        return False

async def persistent_load(urls, num_persistent_requests=300, hold_duration_hours=1, post_data=None, headers=None):
    hold_seconds = hold_duration_hours * 3600
    
    print(f"🔗 PERSISTENT LOAD: {num_persistent_requests} connections holding for {hold_duration_hours} hours")
    print(f"Launch time: {datetime.now().strftime('%H:%M:%S')}")
    
    connector = aiohttp.TCPConnector(
        limit=0,
        limit_per_host=num_persistent_requests,
        keepalive_timeout=hold_seconds + 60,
        enable_cleanup_closed=True
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        print(f"🚀 Launching {num_persistent_requests} long-running requests...")
        
        for i in range(num_persistent_requests):
            url = random.choice(urls)
            task = asyncio.create_task(
                long_running_request(session, url, hold_seconds, post_data, headers)
            )
            tasks.append(task)
        
        start_time = time.time()
        completed = 0
        last_report = start_time
        
        while tasks:
            done, tasks = await asyncio.wait(tasks, timeout=60, return_when=asyncio.FIRST_COMPLETED)
            
            for task in done:
                if task.result():
                    completed += 1
            
            now = time.time()
            if now - last_report >= 60:
                elapsed_min = (now - start_time) / 60
                remaining = len(tasks)
                print(f"[{elapsed_min:.0f}min] Completed: {num_persistent_requests - remaining}/{num_persistent_requests} | "
                      f"Active connections: {remaining}")
                last_report = now
        
        total_time = time.time() - start_time
        print(f"\n✅ ALL {num_persistent_requests} connections closed after {total_time/3600:.1f} hours")

API_ENDPOINTS = [""]
POST_PAYLOAD = {"username": "test", "password": "test"}
HEADERS = {
    "User-Agent": "PersistentLoad/1.0",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache"
}

if __name__ == "__main__":
    asyncio.run(persistent_load(
        API_ENDPOINTS,
        num_persistent_requests=1000, 
        hold_duration_hours=0.01,        
        post_data=POST_PAYLOAD,
        headers=HEADERS
    ))