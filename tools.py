import logging
from openai import OpenAI
from config import Config
import queue
import threading
import time
import socket
config = Config()
Signal = queue.Queue() # 用于线程间通信的信号队列
def reply(qq_message,reply_message,prompt = config.prompt,Signal = Signal):
    global config
    client = config.client[0]
    tools = []
    lrs = [time.time(),0] # last reply timestamp, frequency 
    while True:
        try:
            signal_value = Signal.get()
            if signal_value == "0":
                logging.info("收到继续信号，继续对话")
                if lrs[1] >= config.reply_threshold:
                    logging.error("已经到达频率限制，暂停使用60s")
                    reply_message.put("已经到达频率限制，暂停使用60s")
                    lrs[1] = 0
                    time.sleep(60)
                    qq_message.queue.clear()
                    continue

                if time.time() - lrs[0] <= 60:
                    lrs[1] = lrs[1]+1
                
                else:
                    lrs[1] = 0
                
                
                response = client.chat.completions.create( # Create chat 
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
                    lrs[0] = time.time()
        except Exception as e:
            logging.error(f"发生错误: {e},在线程reply中")
    
        

def auto_kick(kick_signal,auto_kick_channel,Signal = Signal):
    global config
    f = open(config.dictionary, 'r', encoding='utf-8')
    bad_words = f.read().split()
    f.close()
    while True:
        try:
            message = kick_signal.get() #Format : [event.raw_message,event.user_id,event.group_id]
            if "CQ:image" not in message[0]:
                for i in range(len(bad_words)):
                    if bad_words[i] in message[0]:
                        auto_kick_channel.put([True,message[1],message[2],bad_words[i]]) # 发送信号
                        Signal.put("1")
                        logging.warning(f"检测到敏感词: {bad_words[i]}，已发送踢人信号,target = {message[1]} group_id = {message[2]}")
                        continue
                
            auto_kick_channel.put([False])
            Signal.put("0")
            logging.info(f"未检测到敏感词，继续对话,target = {message[1]} group_id = {message[2]}")
        except Exception as e:
            logging.error(f"发生错误: {e},在线程auto_kick中")



def no_spamming(spamming_channel,spamming_signal):
    global config
    threshold = config.spam_threshold
    user_message_count = {}
    temp = {} # 用于记录用户上次发消息的时间戳
    while True:
        try:
            message = spamming_channel.get() #Format : [event.raw_message,event.user_id,event.group_id]
            timestamp = time.time()
            user_id = message[1]
            raw_message = message[0]
            group_id = message[2]

            if user_id in temp:
                if raw_message == temp[user_id][0] and timestamp - temp[user_id][1] <= 10: # 如果消息内容相同且距离上次发消息时间小于10秒
                    if user_id in user_message_count and user_message_count[user_id] >= threshold:
                        spamming_signal.put([True,user_id,group_id]) # 发送信号 
                        user_message_count[user_id] = 0 # 重置计数
                        temp[user_id] = [raw_message, timestamp]
                        logging.warning(f"用户 {user_id} 在群 {group_id} 中，发送了过多相同的消息，已发送禁言信号")
                        continue
                    user_message_count[user_id] = user_message_count.get(user_id,0) + 1
                    logging.warning(f"用户 {user_id} 在群 {group_id} 中，发送了相同的消息，已记录")
                elif timestamp - temp[user_id][1] > 10 or raw_message != temp[user_id][0]:
                    user_message_count[user_id] = 0
            temp[user_id] = [raw_message, timestamp]
        except Exception as e:
            logging.error(f"发生错误: {e},在线程no_spamming中")

                
def cpp_compatible(cpp_post,cpp_get):
    global config
    while True: # 循环连接 
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(config.cpp_server_address)
            s.settimeout(config.socket_timeout)
            s.send(b'hello')
            data = s.recv(config.socket_pack_size).decode('utf-8')
            logging.info('收到回复:'+data)

            if len(data) != 0:
                while True: # 进入通信环节
                    text = cpp_post.get()
                    if any(text[0] == sub for sub in config.support_char): 
                        s.send(text.encode('utf-8'))
                        cpp_get.put(s.recv(config.socket_pack_size).decode('utf-8'))

        
        except (socket.timeout, ConnectionRefusedError, ConnectionResetError): # 当遇到与cpp连接方面的错误时 重试
            logging.error("连接到C++服务器失败，可能是服务器未启动或网络问题,在线程cpp_compatible中")
            logging.info("等待下个连接尝试...")
            time.sleep(config.socket_retry_time)


        except Exception as e:
            logging.error(f"发生错误: {e}")
    
        finally:
            s.close()

        



        