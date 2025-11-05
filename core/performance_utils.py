"""
โมดูลสำหรับการวัดเวลาและปรับปรุงประสิทธิภาพการประมวลผล
"""

import time
import functools
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Dict, List, Tuple, Any, Callable, Optional
import hashlib
import json
import pickle
import os
from collections import defaultdict
import psutil
import gc


class PerformanceTracker:
    """คลาสสำหรับติดตามประสิทธิภาพการประมวลผล"""
    
    def __init__(self):
        self.timings = defaultdict(list)
        self.memory_usage = defaultdict(list)
        self.cpu_usage = defaultdict(list)
        self.start_time = None
        self.end_time = None
    
    def start_timing(self, operation_name: str):
        """เริ่มต้นการวัดเวลา"""
        self.start_time = time.time()
        self._record_system_metrics(operation_name, 'start')
    
    def end_timing(self, operation_name: str):
        """สิ้นสุดการวัดเวลา"""
        if self.start_time is None:
            return None
        
        duration = time.time() - self.start_time
        self.timings[operation_name].append(duration)
        self._record_system_metrics(operation_name, 'end')
        
        return duration
    
    def _record_system_metrics(self, operation_name: str, phase: str):
        """บันทึกเมตริกซ์ระบบ"""
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent()
        
        self.memory_usage[f"{operation_name}_{phase}"].append(memory_percent)
        self.cpu_usage[f"{operation_name}_{phase}"].append(cpu_percent)
    
    def get_average_timing(self, operation_name: str) -> float:
        """ดึงเวลาเฉลี่ยของการดำเนินการ"""
        if operation_name not in self.timings:
            return 0.0
        return sum(self.timings[operation_name]) / len(self.timings[operation_name])
    
    def get_total_timing(self, operation_name: str) -> float:
        """ดึงเวลารวมของการดำเนินการ"""
        if operation_name not in self.timings:
            return 0.0
        return sum(self.timings[operation_name])
    
    def get_stats(self) -> Dict[str, Any]:
        """ดึงสถิติประสิทธิภาพ"""
        stats = {
            'total_operations': len(self.timings),
            'operation_stats': {}
        }
        
        for operation, times in self.timings.items():
            stats['operation_stats'][operation] = {
                'count': len(times),
                'total_time': sum(times),
                'average_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times)
            }
        
        return stats


def timing_decorator(operation_name: str = None):
    """Decorator สำหรับวัดเวลาการทำงานของฟังก์ชัน"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                print(f"⏱️ {name}: {duration:.3f} วินาที")
                return result
            except Exception as e:
                duration = time.time() - start_time
                print(f"❌ {name}: {duration:.3f} วินาที (เกิดข้อผิดพลาด)")
                raise e
        
        return wrapper
    return decorator


class CacheManager:
    """คลาสสำหรับจัดการ cache เพื่อเพิ่มประสิทธิภาพ"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.cache_stats = defaultdict(int)
        
        # สร้างโฟลเดอร์ cache
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, data: Any) -> str:
        """สร้าง cache key จากข้อมูล"""
        if isinstance(data, str):
            return hashlib.md5(data.encode('utf-8')).hexdigest()
        else:
            return hashlib.md5(str(data).encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """ดึงข้อมูลจาก cache"""
        # ลองดึงจาก memory cache ก่อน
        if key in self.memory_cache:
            self.cache_stats['memory_hits'] += 1
            return self.memory_cache[key]
        
        # ลองดึงจาก file cache
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                self.memory_cache[key] = data  # เก็บใน memory cache ด้วย
                self.cache_stats['file_hits'] += 1
                return data
            except Exception:
                pass
        
        self.cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, data: Any, use_file_cache: bool = True):
        """เก็บข้อมูลใน cache"""
        # เก็บใน memory cache
        self.memory_cache[key] = data
        
        # เก็บใน file cache ถ้าต้องการ
        if use_file_cache:
            cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
            except Exception:
                pass
    
    def clear(self):
        """ล้าง cache ทั้งหมด"""
        self.memory_cache.clear()
        
        # ลบไฟล์ cache
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                os.remove(os.path.join(self.cache_dir, filename))
    
    def get_stats(self) -> Dict[str, int]:
        """ดึงสถิติ cache"""
        total_requests = sum(self.cache_stats.values())
        hit_rate = (self.cache_stats['memory_hits'] + self.cache_stats['file_hits']) / total_requests if total_requests > 0 else 0
        
        return {
            'memory_hits': self.cache_stats['memory_hits'],
            'file_hits': self.cache_stats['file_hits'],
            'misses': self.cache_stats['misses'],
            'total_requests': total_requests,
            'hit_rate': hit_rate
        }


class ParallelProcessor:
    """คลาสสำหรับการประมวลผลแบบขนาน"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
    
    def process_texts_parallel(self, texts: List[str], process_func: Callable) -> List[Any]:
        """ประมวลผลข้อความหลายข้อความแบบขนาน"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(process_func, text) for text in texts]
            results = [future.result() for future in futures]
        return results
    
    def process_files_parallel(self, file_paths: List[str], process_func: Callable) -> List[Any]:
        """ประมวลผลไฟล์หลายไฟล์แบบขนาน"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(process_func, file_path) for file_path in file_paths]
            results = [future.result() for future in futures]
        return results
    
    def cleanup(self):
        """ทำความสะอาด resources"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)


class ProgressTracker:
    """คลาสสำหรับติดตามความคืบหน้า"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()
        self.step_times = []
    
    def update(self, step: int = 1, message: str = ""):
        """อัปเดตความคืบหน้า"""
        self.current_step += step
        current_time = time.time()
        
        if self.step_times:
            step_duration = current_time - self.step_times[-1]
            self.step_times.append(current_time)
        else:
            step_duration = 0
            self.step_times.append(current_time)
        
        progress_percent = (self.current_step / self.total_steps) * 100
        elapsed_time = current_time - self.start_time
        
        if self.current_step > 0:
            estimated_total_time = elapsed_time * (self.total_steps / self.current_step)
            remaining_time = estimated_total_time - elapsed_time
        else:
            remaining_time = 0
        
        progress_info = {
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'progress_percent': progress_percent,
            'elapsed_time': elapsed_time,
            'remaining_time': remaining_time,
            'step_duration': step_duration,
            'message': message
        }
        
        # แสดงความคืบหน้า
        self._display_progress(progress_info)
        
        return progress_info
    
    def _display_progress(self, info: Dict[str, Any]):
        """แสดงความคืบหน้า"""
        bar_length = 30
        filled_length = int(bar_length * info['progress_percent'] / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\r{self.description}: |{bar}| {info['progress_percent']:.1f}% "
              f"({info['current_step']}/{info['total_steps']}) "
              f"Elapsed: {info['elapsed_time']:.1f}s "
              f"Remaining: {info['remaining_time']:.1f}s "
              f"{info['message']}", end='', flush=True)
    
    def finish(self, message: str = "Completed"):
        """สิ้นสุดการติดตาม"""
        total_time = time.time() - self.start_time
        print(f"\n✅ {message} in {total_time:.2f} seconds")
        
        return {
            'total_time': total_time,
            'average_step_time': total_time / self.total_steps if self.total_steps > 0 else 0
        }


def optimize_memory():
    """ฟังก์ชันสำหรับเพิ่มประสิทธิภาพหน่วยความจำ"""
    gc.collect()  # ทำ garbage collection
    return psutil.virtual_memory().percent


def get_system_info() -> Dict[str, Any]:
    """ดึงข้อมูลระบบ"""
    return {
        'cpu_count': multiprocessing.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'memory_percent': psutil.virtual_memory().percent,
        'cpu_percent': psutil.cpu_percent(),
        'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
    }


# ตัวแปร global สำหรับ tracking
performance_tracker = PerformanceTracker()
cache_manager = CacheManager()
parallel_processor = ParallelProcessor()


def get_performance_summary() -> Dict[str, Any]:
    """ดึงสรุปประสิทธิภาพ"""
    return {
        'performance_stats': performance_tracker.get_stats(),
        'cache_stats': cache_manager.get_stats(),
        'system_info': get_system_info()
    }
