import random
from openai import OpenAI
from napcat import NapCatClient 


class Config:
    def __init__(self):
        # Global
        self.group_id = 123455 # 群号 ，自行配置
        #AI config
        random_seed = random.randint(0, 1)
        token = []# 请在此处添加你的github PAT，格式如下：token = ["ghp_xxxxxxx", "ghp_yyyyyyy"]
        self.github_PAT = token[random_seed] 
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
        self.dictionary = "bad_words.txt" # 自定义提示词
        
        #no_spamming
        self.spam_threshold = 5

        self.client = NapCatClient(
        ws_url="",
        token=""
        )
# 配置napcat 