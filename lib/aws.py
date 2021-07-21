import boto3

class Aws:
	def __init__(self):
		self.s3 = boto3.resource('s3')
		self.bucket_name = "data.ibeyonde"
		self.bucket = self.s3.Bucket("data.ibeyonde")

	def showUrls(self,uuid,Date):#Date -  YYYY/MM/DD 	
		objs = self.bucket.objects.filter(Prefix=uuid+'/'+Date)
		urls  = list()
		keys = list()
		s_client  = boto3.client('s3')
		for obj in objs:
			keys.append(obj.key)
			urls.append(s_client.generate_presigned_url(ClientMethod='get_object',Params={'Bucket':'data.ibeyonde','Key':obj.key}))

		return keys,urls	

	def showurl(self,url):

		s_client  = boto3.client('s3')
		url = s_client.generate_presigned_url(ClientMethod='get_object',Params={'Bucket':'data.ibeyonde','Key':url})
		return url	