import re
import redis
import asyncio
import aiohttp
import requests
from settings import *


class MyBase:
    """连接redis，作为其他类的父类"""

    def __init__(self):
        self.client = redis.Redis()

    def len_pool(self):
        initial_ip = self.client.scard('ip:initial_ip')
        available_ip = self.client.scard('ip:available_ip')
        return initial_ip, available_ip

    def select(self):
        aip_set = self.client.smembers('ip:available_ip')
        iip_set = self.client.smembers('ip:initial_ip')
        return iip_set, aip_set

    def clear(self):
        count = self.client.scard('ip:available_ip')
        cur, data = self.client.sscan('ip:available_ip', count=count)
        for item in data:
            self.client.srem('ip:available_ip', item)


class SpiderIp(MyBase):
    """爬取链接页面的代理ip"""

    def find_ip(self, start, end):
        """
        请求链接页面
        :param start: 起始页码
        :param end: 终止页码
        :return: None
        """
        for i in range(start, end):
            print('start:', start)
            print('end:', end)
            response = requests.get(url=IP_URL + f'?page={i}', headers=HEADERS)
            text = response.text
            pattern = re.compile(r'<link rel="(.*?)" href="//(\d.*?)">')
            ip_iter = pattern.finditer(text)
            self.save_every_ip(ip_iter)

    def save_every_ip(self, ip_iter):
        """
        将爬取的代理ip保存到redis中
        :param ip_iter: 代理ip
        :return: None
        """
        for i in ip_iter:
            ip = i.group(2)
            self.client.sadd('ip:initial_ip', ip)
            print('添加成功！')


class ScreenIp(MyBase):
    """筛选代理ip"""

    async def screen_ip(self, judge=None):
        """
        使用协程进行异步筛选代理ip
        :return: None
        """
        if judge is None:
            ip = self.client.spop('ip:initial_ip')
        else:
            ip = self.client.spop('ip:available_ip')

        try:
            # 创建session对象
            async with aiohttp.ClientSession() as session:
                if isinstance(ip, bytes):
                    proxy = ip.decode('utf-8')
                    real_proxy = 'http://' + proxy
                try:
                    async with session.get(BAIDU_URL, timeout=5, proxy=real_proxy) as response:
                        # 状态码200代表代理可用
                        if response.status == 200:
                            self.client.sadd('ip:available_ip', ip)
                            print(f'{ip}该ip可用。。。')
                except Exception:
                    print('无效代理')
        except Exception as e:
            print('出现异常：', e)


class GenerateEffectiveIp(MyBase):
    """将可用ip保存到redis的另一个键值对中"""

    def get_ip(self):
        count = self.client.scard('ip:initial_ip')
        get = ScreenIp()
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        tasks = [get.screen_ip() for i in range(count)]
        loop.run_until_complete(asyncio.wait(tasks))
