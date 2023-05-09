from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading
import time

def main():
    # socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if_connect = False
    # host = socket.gethostname()
    # s.connect((host, 9090))

    # 界面
    tk = Tk()
    tk.geometry('1100x600')
    tk.title('Texas')

    def send_msg_format(type, data):
        text = "{\"type\": \"" + type + "\"," + "\"data\": \"" + str(data) + "\"}"
        return text

    # 连接
    def connect(if_connect):
        host = entry_ip.get()
        port = int(entry_port.get())
        nick = entry_nick.get()
        if not if_connect:
            try:
                s.connect((host, port))
                tkinter.messagebox.showinfo('提示', '连接成功')
                if_connect = True
                info_var.set('当前信息：欢迎来到TEXAS，请等待荷官开始游戏')
                t1.start()
                time.sleep(0.5)
                s.send(bytes(send_msg_format(type='nick', data=nick).encode('utf-8')))
            except:
                tkinter.messagebox.showinfo('提示', '连接失败')

    # 数据发送
    def send_action():
        action = select_label.get()
        num = e_raise.get()
        if action == 'raise':
            s.send(bytes(send_msg_format(type=action, data=num).encode('utf-8')))
        else:
            s.send(bytes(send_msg_format(type=action, data=0).encode('utf-8')))

    # ip、端口、昵称
    ip_label = Label(tk, text = '请输入ip地址：', font=('华文中宋', 12)).place_configure(x=20, y=30)
    entry_ip = Entry(tk, width = 18)
    entry_ip.place_configure(x=20, y=60)
    port_label = Label(tk, text = '请输入端口号：', font=('华文中宋', 12)).place_configure(x=20, y=90)
    entry_port = Entry(tk, width = 18)
    entry_port.place_configure(x=20, y=120)
    nick_label = Label(tk, text = '请输入玩家昵称：', font=('华文中宋', 12)).place_configure(x=20, y=150)
    entry_nick = Entry(tk, width = 18)
    entry_nick.place_configure(x=20, y=180)
    button = Button(tk, text='连接', width=10, font=('华文中宋', 12), command=lambda :connect(if_connect)).place_configure(x=35, y=210)

    # block_img
    block = Image.open('block.gif')
    block_render = ImageTk.PhotoImage(image=block)
    # 底牌
    undercard_label = Label(tk, text='底牌', font=('华文中宋', 12)).place_configure(x=285, y=30)
    undercard_img1 = Label(tk, image = block_render).place_configure(x=200, y=50)
    undercard_img2 = Label(tk, image = block_render).place_configure(x=310, y=50)
    # 翻牌圈
    flop_label = Label(tk, text='翻牌', font=('华文中宋', 12)).place_configure(x=585, y=30)
    flop_img1 = Label(tk, image = block_render).place_configure(x=440, y=50)
    flop_img2 = Label(tk, image = block_render).place_configure(x=550, y=50)
    flop_img3 = Label(tk, image = block_render).place_configure(x=660, y=50)
    # 转牌圈
    turn_label = Label(tk, text='转牌', font=('华文中宋', 12)).place_configure(x=825, y=30)
    turn_img = Label(tk, image=block_render).place_configure(x=790, y=50)
    # 河牌圈
    river_label = Label(tk, text='河牌', font=('华文中宋', 12)).place_configure(x=950, y=30)
    river_img = Label(tk, image=block_render).place_configure(x=920, y=50)

    # 玩家信息
    player_label = Label(tk, text='玩家情况（IP&Port、昵称、位置、当局筹码、总筹码、当前行为）', font=('华文中宋', 12)).place_configure(x=20, y=300)
    player_info_var = StringVar()
    player_info_var.set('')
    player_info = Label(tk, textvariable=player_info_var, font=('华文中宋', 12)).place_configure(x=20, y=320)

    # 消息栏
    info_var = StringVar()
    info_var.set('当前信息：')
    info = Label(tk, textvariable=info_var, font=('华文中宋', 12)).place_configure(x=200, y=250)

    # 当前筹码情况
    chip_var = StringVar()
    chip_var.set('已押筹码：')
    l_chip = Label(tk, textvariable=chip_var, font=('华文中宋', 12)).place_configure(x=750, y=250)
    all_chip_var = StringVar()
    all_chip_var.set('剩余筹码：')
    l_all_chip = Label(tk, textvariable=all_chip_var, font=('华文中宋', 12)).place_configure(x=750, y=280)

    # 操作部分
    select_label = StringVar()
    r_call = Radiobutton(tk, text = 'call（跟注）', variable = select_label, value = 'call', font=('华文中宋', 12)).place_configure(x=700, y=360)
    r_check = Radiobutton(tk, text = 'check（过牌）', variable = select_label, value = 'check', font=('华文中宋', 12)).place_configure(x=700, y=390)
    r_fold = Radiobutton(tk, text = 'fold（弃牌）', variable = select_label, value = 'fold', font=('华文中宋', 12)).place_configure(x=700, y=420)
    r_raise = Radiobutton(tk, text = 'raise（加注）', variable = select_label, value = 'raise', font=('华文中宋', 12)).place_configure(x=700, y=450)
    r_allin = Radiobutton(tk, text = 'all-in（全押）', variable = select_label, value = 'allin', font=('华文中宋', 12)).place_configure(x=700, y=480)
    l_raise = Label(tk, text='加注筹码量：', font=('华文中宋', 12)).place_configure(x=900, y=360)
    e_raise = Entry(tk, width=15)
    e_raise.place_configure(x=900, y=410)
    button2 = Button(tk, text='确定', height=2, width=10, font=('华文中宋', 12), command=lambda :send_action()).place_configure(x=900, y=460)

    # 注意事项
    l_tips = Label(tk, text='注意：只有raise（加注）需要输入筹码，其他选择不用', font=('华文中宋', 12), fg='blue').place_configure(x=660, y=550)

    # 监听，其他img
    def receive():
        while True:
            data = s.recv(1024).decode('utf-8')
            try:
                data_dic = eval(data)
                if data_dic['type'] == 'start':
                    undercard_img1 = Label(tk, image=block_render).place_configure(x=200, y=50)
                    undercard_img2 = Label(tk, image=block_render).place_configure(x=310, y=50)
                    flop_img1 = Label(tk, image=block_render).place_configure(x=440, y=50)
                    flop_img2 = Label(tk, image=block_render).place_configure(x=550, y=50)
                    flop_img3 = Label(tk, image=block_render).place_configure(x=660, y=50)
                    turn_img = Label(tk, image=block_render).place_configure(x=790, y=50)
                    river_img = Label(tk, image=block_render).place_configure(x=920, y=50)
                elif data_dic['type'] == 'flop':
                    card_list = data_dic['data']
                    flop1 = Image.open('./cards/' + card_list[0] + '.jpg')
                    flop1_render = ImageTk.PhotoImage(image=flop1)
                    flop_img1 = Label(tk, image=flop1_render).place_configure(x=440, y=50)
                    flop2 = Image.open('./cards/' + card_list[1] + '.jpg')
                    flop2_render = ImageTk.PhotoImage(image=flop2)
                    flop_img1 = Label(tk, image=flop2_render).place_configure(x=550, y=50)
                    flop3 = Image.open('./cards/' + card_list[2] + '.jpg')
                    flop3_render = ImageTk.PhotoImage(image=flop3)
                    flop_img1 = Label(tk, image=flop3_render).place_configure(x=660, y=50)
                elif data_dic['type'] == 'chip':
                    chip_var.set('已押筹码：' + str(data_dic['data']))
                elif data_dic['type'] == 'all_chip':
                    all_chip_var.set('剩余筹码：' + str(data_dic['data']))
                elif data_dic['type'] == 'turn':
                    card_list = data_dic['data']
                    turn = Image.open('./cards/' + card_list[0] + '.jpg')
                    turn_render = ImageTk.PhotoImage(image=turn)
                    turn_img = Label(tk, image=turn_render).place_configure(x=790, y=50)
                elif data_dic['type'] == 'river':
                    card_list = data_dic['data']
                    river = Image.open('./cards/' + card_list[0] + '.jpg')
                    river_render = ImageTk.PhotoImage(image=river)
                    river_img = Label(tk, image=river_render).place_configure(x=920, y=50)
                elif data_dic['type'] == 'info':
                    text = '当前信息：' + data_dic['data']
                    info_var.set(text)
                elif data_dic['type'] == 'msg':
                    tkinter.messagebox.showinfo('info', data_dic['data'])
                elif data_dic['type'] == 'port':
                    ip_label = Label(tk, text='我的ip及端口号：' + str(data_dic['data']), font=('华文中宋', 12)).place_configure(x=200, y=220)
                elif data_dic['type'] == 'status':
                    list_data = list(data_dic['data'])
                    text = ''
                    for i in list_data:
                        split_i = str(i).replace('(', '').replace(')', '').split(',')
                        for j in range(0, len(split_i)):
                            text += split_i[j]
                            if j != 0:
                                text += '\t'
                        text += '\n'
                    player_info_var.set(text)
                elif data_dic['type'] == 'show':
                    text = ''
                    for i in data_dic['data'].split('。'):
                        text += i
                        text += '\n'
                    show_off_var = StringVar()
                    show_off_var.set(text)
                    show_off = Label(tk, textvariable=show_off_var, font=('华文中宋', 12)).place_configure(x=20,y=480)
                elif data_dic['type'] == 'under':
                    list_data = list(data_dic['data'])
                    undercard1 = Image.open('./cards/' + list_data[0] + '.jpg')
                    undercard1_render = ImageTk.PhotoImage(image=undercard1)
                    undercard_img1 = Label(tk, image = undercard1_render).place_configure(x=200, y=50)
                    undercard2 = Image.open('./cards/' + list_data[1] + '.jpg')
                    undercard2_render = ImageTk.PhotoImage(image=undercard2)
                    undercard_img2 = Label(tk, image = undercard2_render).place_configure(x=310, y=50)
            except:
                print(data)
                print('error!', 'incorrect data format')

    t1 = threading.Thread(target=receive, daemon=True)
    mainloop()

if __name__ == '__main__':
    main()