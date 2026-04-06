import random
from openai import OpenAI


class Config:
    def __init__(self):
        # Global
        self.group_id = int # 输入你的群号，类型为int
        self.ws_url="" # 输入你的ws地址，格式为ws://ip:port
        self.token="" # 输入你的token，格式为字符串, 即前文"配置napcat"中的token
        self.support_name = [""] # 配置ai所支持的呼出名称


        #AI config
        self.github_PAT = "" #请勿轻易修改，此为api的访问令牌,输入你的github_PAT，格式为字符串

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
        self.dictionary = "bad_words.txt" # 输入你的敏感词文件路径，格式为字符串 , 且每个敏感词使用空格分隔开
        
        #no_spamming
        self.spam_threshold = 5

        #cpp_compatible
        self.cpp_server_address = ()
        self.socket_timeout = 10 # seconds
        self.socket_retry_time = 10 # seconds
        self.socket_pack_size = 1024 # bytes
        self.support_char = []