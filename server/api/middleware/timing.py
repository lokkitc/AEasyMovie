import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from typing import Callable
import statistics

logger = logging.getLogger(__name__)

class TimingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_times = {}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Сохраняем время выполнения для статистики
        if path not in self.request_times:
            self.request_times[path] = []
        self.request_times[path].append(process_time)
        
        # Логируем детальную информацию
        logger.info(
            f"Request: {method} {path}\n"
            f"Time: {process_time:.3f}s\n"
            f"Avg time: {statistics.mean(self.request_times[path]):.3f}s\n"
            f"Min time: {min(self.request_times[path]):.3f}s\n"
            f"Max time: {max(self.request_times[path]):.3f}s"
        )
        
        return response 