import random
from openai import OpenAI


class Config:
    def __init__(self):
        # Global
        self.group_id = int # 群号
        self.ws_url=""
        self.token=""
        self.support_name = [""] # 配置ai所支持的呼出名称


        #AI config
        self.github_PAT = "" #请勿轻易修改，此为api的访问令牌 

        self.reply_threshold = 5 # 回复频率限制，单位为次/分钟，防止过于频繁的回复导致被封禁
        # 提示词
        self.prompt = """ 
        """

        self.client = [
            OpenAI(
            base_url = "https://models.github.ai/inference",
            api_key = self.github_PAT,
            default_query = {
                "api-version": "2024-08-01-preview",
            },
        )
        ]
        # OpenAI client 配置 

        #auto_kick
        self.dictionary = "bad_words.txt"
        
        #no_spamming
        self.spam_threshold = 5

        #cpp_compatible
        self.cpp_server_address = ()
        self.socket_timeout = 10 # seconds
        self.socket_retry_time = 10 # seconds
        self.socket_pack_size = 1024 # bytes
        self.support_char = []