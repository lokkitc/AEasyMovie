import asyncio
import aiohttp
import time
from statistics import mean, median, stdev
from typing import List, Dict

async def make_request(session: aiohttp.ClientSession, url: str) -> float:
    start_time = time.time()
    async with session.get(url) as response:
        await response.text()
        return time.time() - start_time

async def load_test(url: str, num_requests: int = 100, concurrent: int = 10) -> Dict:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_requests):
            tasks.append(make_request(session, url))
            if len(tasks) >= concurrent:
                await asyncio.gather(*tasks)
                tasks = []
        
        if tasks:
            await asyncio.gather(*tasks)
        
        times = [task.result() for task in tasks]
        
        return {
            "total_requests": num_requests,
            "concurrent_requests": concurrent,
            "min_time": min(times),
            "max_time": max(times),
            "mean_time": mean(times),
            "median_time": median(times),
            "stdev_time": stdev(times) if len(times) > 1 else 0
        }

if __name__ == "__main__":
    # Пример использования
    url = "http://localhost:8000/api/users/"
    results = asyncio.run(load_test(url))
    
    print("\nРезультаты нагрузочного тестирования:")
    print(f"Всего запросов: {results['total_requests']}")
    print(f"Конкурентных запросов: {results['concurrent_requests']}")
    print(f"Минимальное время: {results['min_time']:.3f}с")
    print(f"Максимальное время: {results['max_time']:.3f}с")
    print(f"Среднее время: {results['mean_time']:.3f}с")
    print(f"Медианное время: {results['median_time']:.3f}с")
    print(f"Стандартное отклонение: {results['stdev_time']:.3f}с") 