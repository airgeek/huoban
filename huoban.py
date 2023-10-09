from urllib.parse import urlparse, parse_qs
import re
import base64
import requests


class HUOBAN:
	def __init__(self,share_url):
		self.domain_encode = 'aHVvYmFuLmNvbQ==' #简单bs64一下域名,低调使用
		self.domain = base64.b64decode(self.domain_encode.encode()).decode()
		self.__set_default(share_url) #初始化参数
		self.__get_tk() #获取令牌
		self.__get_columns() #获取列表

	def __set_default(self,share_url):
		'''根据共享链接,提取出基本参数'''
		parsed_url = urlparse(share_url)
		query_params = parse_qs(parsed_url.query)
		self.table_id = re.findall(r'\d+',share_url)[0]
		self.table_share_id = query_params['table_share_id'][0]
		self.share_id = query_params['share_id'][0]
		self.secret = query_params['secret'][0]

	def __get_tk(self):
		'''获取令牌'''
		url = 'https://api.'+self.domain+'/v2/ticket'
		c = {
			'share_id':self.share_id,
			'secret':self.secret
			}
		rsp = requests.post(url,json=c).json()
		ticket = rsp['ticket']
		self.ticket = ticket

	def __get_columns(self):
		''''''
		url = f'https://api.'+self.domain+'/v2/table_share/'+self.table_share_id
		rsp = requests.get(url,headers={'X-Huoban-Ticket':self.ticket,'X-Huoban-Return-Fields':'["*", "table", "has_created"]'}).json()
		columns_id = {i['field_id']:i['name'] for i in rsp['table']['fields']}
		columns_name = {value:key for key,value in columns_id.items()}
		self.columns_id = columns_id #以id为键
		self.columns_name = columns_name #以列名为键

	def get_items(self,rows=100):
		'''取回一定的行数'''
		url = f'https://api.'+self.domain+'/v2/h5/item/table/'+self.table_id+'/filter'
		c = {"limit":rows,"offset":0}
		rsp = requests.post(url,json=c,headers={'X-Huoban-Ticket':self.ticket}).json()
		return rsp['items']

	def edit_item(self,item_id:int,c:dict):
		'''编辑某行'''
		url = f'https://api.'+self.domain+f'/v2/item/{item_id}'
		c = {"fields":c}
		try:
			rsp = requests.put(url,json=c,headers={'X-Huoban-Ticket':self.ticket},timeout=5).json()
		except requests.exceptions.ConnectTimeout:
			return {'ret':0,'msg':'超时'}
		except requests.exceptions.JSONDecodeError:
			return {'ret':0,'msg':'rsp结果json格式化错误'}
		if 'message' in rsp:
			return {'ret':0,'msg':rsp['message']}
		if 'item_id' in rsp:
			return {'ret':1,'msg':'更新成功'}

	def add_item(self,c:dict):
		'''新增行
		c = {self.key:value,} 例如 {'2200000446658576':'abc'}
		'''
		url = f'https://api.'+self.domain+'/v2/h5/item/table/'+self.table_id
		c = {"fields":c}
		try:
			rsp = requests.post(url,json=c,headers={'X-Huoban-Ticket':self.ticket},timeout=5).json()
		except requests.exceptions.ConnectTimeout:
			return {'ret':0,'msg':'超时'}
		except requests.exceptions.JSONDecodeError:
			return {'ret':0,'msg':'rsp结果json格式化错误'}
		if 'message' in rsp:
			return {'ret':0,'msg':rsp['message']}
		if 'item_id' in rsp:
			return {'ret':1,'msg':'新增成功'}
