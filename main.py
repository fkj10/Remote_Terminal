import asyncio
from napcat import NapCatClient
import napcat
import logging
import queue
import threading
import tools
import datetime
import os
from config import Config

# 部分注释来自Copilot 使用中文
# 部分注释来自_cmd_block 使用英文
# 至于为什么，可能是我懒得切换输入法了((( 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#Config logging format

#reply 功能所需queue
message = queue.Queue() # main -> reply
reply_message = queue.Queue() # main <- reply

# auto_kick 功能所需queue
kick_signal = queue.Queue() #main -> auto_kick 
auto_kick_channel = queue.Queue() #main <- auto_kick 
# no_spamming 功能所需queue
spamming_signal = queue.Queue() # main <- no_spamming
spamming_channel = queue.Queue() # main -> no_spamming 

# cpp_compatible 功能所需queue
cpp_get = queue.Queue() # main <- cpp_compatible ( <- cpp_server )
# Get cpp server return ,executing napcat-sdk function  
cpp_post = queue.Queue() # main -> cpp_compatible (-> cpp_server )
# Sending QQ message (and info ) to cpp Server 

support_name = Config().support_name 
# 配置ai所支持的呼出名称
# 配置ai所支持的呼出名称
# 即使用哪些名字可以调用reply
      

threading.Thread(target = tools.reply, args=[message,reply_message] ).start() # Start reply thread
threading.Thread(target = tools.auto_kick, args=[kick_signal,auto_kick_channel] ).start() # Start auto_kick thread
threading.Thread(target = tools.no_spamming, args=[spamming_channel,spamming_signal] ).start() # Start no_spamming thread

client = NapCatClient(
    ws_url=Config().ws_url,
    token=Config().token
)
# 配置napcat 

async def main():
    logging.info("正在连接到 NapCat...")
    async with client:
        logging.info(f"连接成功！当前登录账号: {client.self_id}")
        # 3. 循环接收事件
        async for event in client:
            if isinstance(event, (napcat.types.GroupMessageEvent)):
                logging.info(f"收到消息: {event.raw_message}")
                ###
                #在此处配置要放入哪些队列
                ###
                
                kick_signal.put([event.raw_message,event.user_id,event.group_id])
                spamming_signal.put([event.raw_message,event.user_id,event.group_id])
                logging.info(f"消息已放入队列: {event.raw_message}")

                if any(sub in event.raw_message for sub in support_name):
                    message.put(event.raw_message)
                    reply_result = reply_message.get()
                    await client.send_msg(message_type="group", group_id = event.group_id, message=str("@"+event.sender.nickname)+"\n"+reply_result)
                    logging.info(f"回复已发送")

def sub_thread(kick_signal,spamming_signal,client):
    async def main_sub():
        try:
            # 此线程用于管理群 直接和no_spamming和auto_kick通信
            async with client:
                while True:
                    #spamming_signal.put([True,user_id,group_id]) # 发送信号 
                    #kick_signal.put([True,message[1],message[2]])
                    #Format : [event.raw_message,event.user_id,event.group_id]
                    kick_info = kick_signal.get()
                    ban_info = spamming_signal.get()
                    if kick_info[0] == True:
                        for user in client.get_group_member_list(Config().group_id): # 获取群成员列表 用于 auto_kick 功能
                            if user.user_id == kick_info[1] and user.group_id == kick_info[2]: # 如果用户在群里了 就执行踢人了
                                logging.info(f"用户 {kick_info[1]} 在群 {kick_info[2]} 中，准备执行踢人操作")
                                await client.set_group_kick(group_id = kick_info[2], user_id = kick_info[1])
                                logging.info(f"已踢人: user_id={kick_info[1]} group_id={kick_info[2]}")

                    if ban_info[0] == True:
                        for user in client.get_group_shut_list(Config().group_id): # 获取群禁言列表 用于 no_spamming 功能
                            if user.user_id == ban_info[1] and user.group_id == ban_info[2]: # 如果用户已经在禁言列表里了 就不重复禁言了
                                logging.info(f"用户 {ban_info[1]} 已经在群 {ban_info[2]} 的禁言列表里了，跳过禁言")
                            
                        else:
                            await client.set_group_ban(group_id = ban_info[2], user_id = ban_info[1], duration=120)
                            logging.info(f"已禁言: user_id={ban_info[1]} group_id={ban_info[2]} duration=120s")
        except Exception as e:
            logging.error(f"发生错误: {e},在线程sub_thread中")
                
    asyncio.run(main_sub())


if __name__ == "__main__":
    asyncio.run(main())
    threading.Thread(target = sub_thread, args=[kick_signal,spamming_signal,client] ).start()
