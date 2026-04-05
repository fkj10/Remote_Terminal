import logging
from openai import OpenAI
from config import Config
import queue
import threading
import time

Signal = queue.Queue() # 用于线程间通信的信号队列
def reply(qq_message,reply_message,prompt = Config().prompt,Signal = Signal):
    client = Config().client[0]
    tools = []
    while True:
        signal_value = Signal.get()
        if signal_value == "0":
            logging.info("收到继续信号，继续对话")
            response = client.chat.completions.create(
                messages = [
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": qq_message.get(),
                    }
                ],
                model = "openai/gpt-4o",
                tools = tools,
                temperature = 1,
                top_p = 1,
            )

            if response.choices[0].message.tool_calls:
                pass
            else:
                content = response.choices[0].message.content
                logging.info(f"模型回复: {content}")
                reply_message.put(content)
    
        

def auto_kick(kick_signal,auto_kick_channel,Signal = Signal):
    f = open(Config().dictionary, 'r', encoding='utf-8')
    bad_words = f.read().split()
    f.close()
    while True:
        message = kick_signal.get() #Format : [event.raw_message,event.user_id,event.group_id]
        for i in range(len(bad_words)):
            if bad_words[i] in message[0]:
                auto_kick_channel.put([True,message[1],message[2],bad_words[i]]) # 发送信号
                Signal.put("1")
                break
                
        auto_kick_channel.put([False])
        Signal.put("0")



def no_spamming(spamming_channel,spamming_signal):
    threshold = Config().spam_threshold
    user_message_count = {}
    temp = {} # 用于记录用户上次发消息的时间戳
    while True:
        message = spamming_channel.get() #Format : [event.raw_message,event.user_id,event.group_id]
        timestamp = time.time()
        user_id = message[1]
        message = message[0]
        group_id = message[2]

        if user_id in temp:
            if message == temp[user_id][0] and timestamp - temp[user_id][1] < 10: # 如果消息内容相同且距离上次发消息时间小于10秒
                if user_id in user_message_count:
                    if user_message_count[user_id] >= threshold:
                        spamming_signal.put([True,user_id,group_id]) # 发送信号 
                        user_message_count[user_id] = 0 # 重置计数
                    else:
                        user_message_count[user_id] += 1
                else:
                    user_message_count[user_id] = 2 # 从2开始计数，因为已经发了两条相同的消息了
        else:
            temp[user_id] = [message, timestamp]
                



        