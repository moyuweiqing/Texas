import socket
import queue
import threading
import time
import os
import random
import Texas

# socket编程准备
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
serversocket.bind((host, 9090))
serversocket.listen(8)
# 存放已连接的对象
clients = []
addrs = []

# 开启游戏
texas = Texas.Texas()
texas.init_cards()
action_flag = False         # 用户操作的标识
now_chip = texas.last_chip  # 当前筹码

# 获取卡片列表
card_list = os.listdir('./cards/')

# 接收新的对象
def init():
    def send_msg_format(type, data):
        text = "{'type': '" + type + "'," + "'data': '" + data + "'}"
        return text

    while True:
        client, addr = serversocket.accept()  # 阻塞线程
        if client not in clients:
            # client.send(bytes(send_msg_format(type='info', data='欢迎来到TEXAS，请等待荷官开始游戏').encode('utf-8')))
            clients.append(client)
            addrs.append(addr)
            player = Texas.Player(addr, addr, 300)
            texas.add_player(player)

            t = threading.Thread(target=receive, args=(client, addr))
            t.start()

# 发送玩家状态信息
def send_status_info():
    def send_msg_format(type, data):
        text = "{\"type\": \"" + type + "\"," + "\"data\": " + str(data) + "}"
        return text

    while True:
        time.sleep(0.5)
        # 分开发送，防止格式不一致
        for i in range(0, len(clients)):
            clients[i].send(bytes(send_msg_format(type='status', data=texas.get_status_info()).encode('utf-8')))
            time.sleep(0.1)
            clients[i].send(bytes(send_msg_format(type='port', data=str(addrs[i])).encode('utf-8')))
            time.sleep(0.1)
            clients[i].send(bytes(send_msg_format(type='chip', data=str(texas.playerlist[i].now_chip)).encode('utf-8')))
            time.sleep(0.1)
            clients[i].send(bytes(send_msg_format(type='all_chip', data=str(texas.playerlist[i].chip)).encode('utf-8')))

# 获取玩家发送的信息
def receive(client, addr):
    global action_flag, now_chip
    def send_msg_format(type, data):
        text = "{\"type\": \"" + type + "\"," + "\"data\": \"" + str(data) + "\"}"
        return text

    while True:
        if client in clients:
            data = client.recv(1024).decode('utf-8')
            try:
                # 字符串转字典
                data_dic = eval(data)
                # 昵称信息
                if data_dic['type'] == 'nick':
                    for i in texas.playerlist:
                        if i.id == addr:
                            i.change_name(str(data_dic['data']).replace("'", ''))
                # 桌面操作信息
                if data_dic['type'] in ['raise', 'check', 'fold', 'call', 'allin']:
                    action_chip = int(data_dic['data'])
                    for i in texas.playerlist:
                        if i.id == addr and addr == texas.playerlist[now_location].id:
                            now_chip = texas.get_max_chip()
                            if data_dic['type'] == 'fold':      # fold 弃牌
                                i.change_chip('fold', 0)
                                action_flag = True
                                client.send(bytes(send_msg_format(type='info', data='请等待其他玩家行动').encode('utf-8')))
                            if data_dic['type'] == 'allin':     # allin 全押
                                i.change_chip('allin', i.chip)
                                action_flag = True
                                client.send(bytes(send_msg_format(type='info', data='请等待其他玩家行动').encode('utf-8')))
                            if data_dic['type'] == 'check':     # check 过牌
                                if i.now_chip != now_chip:
                                    client.send(bytes(send_msg_format(type='msg', data='你check什么check').encode('utf-8')))
                                else:
                                    i.change_chip('check', 0)
                                    action_flag = True
                                    client.send(bytes(send_msg_format(type='info', data='请等待其他玩家行动').encode('utf-8')))
                            if data_dic['type'] == 'raise':     # raise 加注
                                if i.chip < action_chip or now_chip > i.now_chip + action_chip:
                                    client.send(bytes(send_msg_format(type='msg', data='筹码不足').encode('utf-8')))
                                else:
                                    i.change_chip('raise', action_chip)
                                    action_flag = True
                                    client.send(bytes(send_msg_format(type='info', data='请等待其他玩家行动').encode('utf-8')))
                            if data_dic['type'] == 'call':      # call 跟注
                                if i.chip < texas.last_chip:
                                    client.send(bytes(send_msg_format(type='msg', data='筹码不足').encode('utf-8')))
                                else:
                                    i.change_chip('call', now_chip - i.now_chip)
                                    action_flag = True
                                    client.send(bytes(send_msg_format(type='info', data='请等待其他玩家行动').encode('utf-8')))
                        elif addr != texas.playerlist[now_location].id:
                            print(addr, i.id, texas.playerlist[now_location].id)
                            client.send(bytes(send_msg_format(type='msg', data='没到你呢，别着急').encode('utf-8')))
            except:
                print(data)
                print('error!', 'incorrect data format')

# 发送消息格式化
def send_msg_format(type, data):
    text = "{'type': '" + type + "'," + "'data': " + data + "}"
    return text

# 设置多线程
t1 = threading.Thread(target=init)
t1.start()

t2 = threading.Thread(target=send_status_info)
t2.start()

if __name__ == '__main__':
    # 开始游戏
    start = False
    now_location = -1  # 当前位置
    while not start:
        num = input("输入1开始游戏：")
        if num == '1':
            start = True
    # 开始一局游戏
    while start:
        if_finished = False  # 是否结束游戏
        texas.make_player_init()
        # 洗牌
        for i in range(0, len(clients)):
            clients[i].send(bytes(send_msg_format(type='start', data=str(addrs[i])).encode('utf-8')))
        # 角色选择和获取起叫顺序
        texas.choose_act()
        texas.get_call_list()
        # 发位置和底牌
        texas.send_cards()
        for i in range(0, len(clients)):
            clients[i].send(bytes(send_msg_format(type='port', data=str(addrs[i])).encode('utf-8')))                          # 发送位置
            time.sleep(0.1)
            clients[i].send(bytes(send_msg_format(type='under', data=str(texas.playerlist[i].cards)).encode('utf-8')))        # 发底牌
        time.sleep(0.2)
        # 第一轮叫牌
        now_chip = texas.last_chip  # 当前筹码
        judge = False
        cnt = 0
        while judge == False and if_finished == False:
            for i in texas.call_list:
                if texas.if_last_player():
                    name = texas.check_out()
                    for j in texas.call_list:
                        clients[i].send(bytes(send_msg_format(type='info', data=f'\"游戏结束，赢家是：{name}\"').encode('utf-8')))
                        time.sleep(0.2)
                    if_finished = True
                    break
                if texas.playerlist[i].action != 'fold':
                    action_flag = False  # 用户操作的标识
                    now_location = i
                    while action_flag == False:
                        clients[i].send(bytes(send_msg_format(type='info', data='\"到你了\"').encode('utf-8')))
                        time.sleep(0.5)
                cnt += 1
                if cnt > len(texas.call_list):
                    judge = texas.if_thesame_chip()
            judge = texas.if_thesame_chip()
        if if_finished == False:
            for client in clients:
                client.send(bytes(send_msg_format(type='info', data='\"请等待发翻牌\"').encode('utf-8')))
            time.sleep(2)
            texas.send_flop()
            for client in clients:
                client.send(bytes(send_msg_format(type='flop', data=str(texas.flop)).encode('utf-8')))

        # 转牌圈
        texas.get_call_list()
        # 第二轮叫牌
        now_chip = texas.last_chip  # 当前筹码
        judge = False
        cnt = 0
        while judge == False and if_finished == False:
            for i in texas.call_list:
                if texas.if_last_player():
                    name = texas.check_out()
                    for j in texas.call_list:
                        clients[i].send(bytes(send_msg_format(type='info', data=f'\"游戏结束，赢家是：{name}\"').encode('utf-8')))
                        time.sleep(0.2)
                    if_finished = True
                    break
                if texas.playerlist[i].action != 'fold':
                    action_flag = False  # 用户操作的标识
                    now_location = i
                    while action_flag == False:
                        clients[i].send(bytes(send_msg_format(type='info', data='\"到你了\"').encode('utf-8')))
                        time.sleep(0.5)
                cnt += 1
                if cnt > len(texas.call_list):
                    judge = texas.if_thesame_chip()
            judge = texas.if_thesame_chip()
        if if_finished == False:
            for client in clients:
                client.send(bytes(send_msg_format(type='info', data='\"请等待发转牌\"').encode('utf-8')))
            time.sleep(2)
            texas.send_turn()
            for client in clients:
                client.send(bytes(send_msg_format(type='turn', data=str(texas.turn)).encode('utf-8')))

        # 河牌圈
        texas.get_call_list()
        # 第三轮叫牌
        now_chip = texas.last_chip  # 当前筹码
        judge = False
        cnt = 0
        while judge == False and if_finished == False:
            for i in texas.call_list:
                if texas.if_last_player():
                    name = texas.check_out()
                    for j in texas.call_list:
                        clients[i].send(bytes(send_msg_format(type='info', data=f'\"游戏结束，赢家是：{name}\"').encode('utf-8')))
                        time.sleep(0.2)
                    if_finished = True
                    break
                if texas.playerlist[i].action != 'fold':
                    action_flag = False  # 用户操作的标识
                    now_location = i
                    while action_flag == False:
                        clients[i].send(bytes(send_msg_format(type='info', data='\"到你了\"').encode('utf-8')))
                        time.sleep(0.5)
                cnt += 1
                if cnt > len(texas.call_list):
                    judge = texas.if_thesame_chip()
            judge = texas.if_thesame_chip()
        if if_finished == False:
            for client in clients:
                client.send(bytes(send_msg_format(type='info', data='\"请等待发河牌\"').encode('utf-8')))
            time.sleep(2)
            texas.send_river()
            for client in clients:
                client.send(bytes(send_msg_format(type='river', data=str(texas.river)).encode('utf-8')))

        if if_finished:
            for client in clients:
                client.send(bytes(send_msg_format(type='info', data=f'\"游戏结束，赢家是：{name}，请等待荷官开始下一把游戏\"').encode('utf-8')))

        # 第四轮叫牌
        now_chip = texas.last_chip  # 当前筹码
        judge = False
        cnt = 0
        while judge == False and if_finished == False:
            for i in texas.call_list:
                if texas.if_last_player():
                    name = texas.check_out()
                    for j in texas.call_list:
                        clients[i].send(
                            bytes(send_msg_format(type='info', data=f'\"游戏结束，赢家是：{name}\"').encode('utf-8')))
                        time.sleep(0.2)
                    if_finished = True
                    break
                if texas.playerlist[i].action != 'fold':
                    action_flag = False  # 用户操作的标识
                    now_location = i
                    while action_flag == False:
                        clients[i].send(bytes(send_msg_format(type='info', data='\"到你了\"').encode('utf-8')))
                        time.sleep(0.5)
                cnt += 1
                if cnt > len(texas.call_list):
                    judge = texas.if_thesame_chip()
            judge = texas.if_thesame_chip()

        # show off
        text = ''
        for i in texas.playerlist:
            if i.action != 'fold':
                text += '玩家：' + i.player_name + '的牌面为' + str(i.cards)
                text += '。'
        for i in texas.call_list:
            clients[i].send(bytes(send_msg_format(type='show', data=f'\"{text}\"').encode('utf-8')))

        # 比较大小
        player_name = input('请输入赢家昵称：')
        for i in texas.playerlist:
            if i.player_name != player_name:
                i.action = 'fold'
        name = texas.check_out()
        for i in texas.call_list:
            clients[i].send(bytes(send_msg_format(type='info', data=f'\"游戏结束，赢家是：{name}\"').encode('utf-8')))
            time.sleep(0.2)
        if_finished = True

        # 游戏结束
        num = input("输入1开始游戏，输入2结束游戏：")
        if num == '1':
            start = True
            for client in clients:
                client.send(bytes(send_msg_format(type='info', data='\"请等待游戏开始\"').encode('utf-8')))
            time.sleep(5)
        elif num == '2':
            start = False
            for client in clients:
                client.send(bytes(send_msg_format(type='info', data='\"游戏结束，请玩家各自结算"').encode('utf-8')))