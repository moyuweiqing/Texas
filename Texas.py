
import random

class Player:
    def __init__(self, player_name, id, chip):
        '''
        玩家初始化
        :param player_name: 玩家姓名
        :param id: 玩家id，即座位号
        :param chip: 玩家筹码数量
        '''
        self.player_name = player_name
        self.id = id
        self.chip = chip        # 剩余的筹码数量
        self.game_init()        # 游戏初始化
    def game_init(self):
        self.now_chip = 0       # 当前游戏的筹码数量
        self.act = ''           # 当前游戏的角色： sb: small blind 小盲; bb: big blind 大盲; bk: banker 庄家; 其它则为空
        self.action = ''        # 当前游戏的游戏行为：Call：跟注; Fold：收牌; Check：过牌; All-in：全押; Raise: 加注
        self.cards = []         # 当前游戏的卡牌
    def get_act(self, act='', now_chip=0):
        '''
        获取角色
        :param act: 角色，sb bb bk null
        :param now_chip:  开局下筹码
        :return:
        '''
        self.act = act
        self.now_chip = now_chip
        self.chip -= now_chip
    def get_action(self, last_chip):
        '''
        :return:
        '''
        now_chip = input('上家筹码：' + str(last_chip) + '，你当前已投入筹码：' + str(self.now_chip) + '，剩余筹码' + str(self.chip) + '，请输入需要追加的筹码：（ -1 为弃牌，0 为过牌）：')
        while len(now_chip) <= 0 or (''.join(list(filter(str.isdigit, now_chip))) != now_chip and now_chip != '-1'):
            now_chip = input('请重新输入：')
        while ( not (int(now_chip) == -1 or ((int(now_chip) >= 0 and int(now_chip) <= self.chip) and int(now_chip) % 5 == 0))) or (int(now_chip) == 0 and last_chip != self.now_chip):
            now_chip = input('请重新输入：')

        if now_chip == '-1':
            self.change_chip('fold', 0)
            return last_chip
        now_chip = int(now_chip)
        if self.now_chip == last_chip and now_chip == 0:
            self.change_chip('Check', 0)
        elif self.now_chip + now_chip == last_chip:
            self.change_chip('Call', now_chip)
        elif self.now_chip + now_chip > last_chip and now_chip < self.chip:
            self.change_chip('Raise', now_chip)
        elif self.now_chip + now_chip > last_chip and now_chip == self.chip:
            self.change_chip('All-in', now_chip)
        return self.now_chip
    def change_name(self, name):
        self.player_name = name
    def change_chip(self, action, now_chip):
        '''
        :param action: 当前动作
        :param now_chip: 添加的筹码
        :return:
        '''
        self.action = action
        self.now_chip += now_chip
        self.chip -= now_chip
    def check_out(self, check_chip):
        '''
        结算
        :param check_chip: 结算筹码
        :return:
        '''
        self.chip += check_chip
    def get_cards(self, cards):
        '''
        获取卡
        :param cards:
        :return:
        '''
        self.cards = cards
        # print(self.cards)



class Texas:
    def __init__(self):
        '''
        初始化
        '''
        self.all_init()
    def all_init(self):
        self.carddic = {}                           # 所有牌的状态
        self.cardlist = []                          # 所有牌的列表
        self.playerlist = []                        # 玩家列表
        self.banker_index = -1                      # 庄家位置
        self.sb_index = 0                           # 小盲位置
        self.bb_index = 1                           # 大盲位置
        self.min_chip = 5                           # 最低追加筹码量，也即小盲位筹码量
        self.last_chip = self.min_chip * 2          # 当前的最大筹码数，初始为大盲
        self.call_list = []                         # 起叫顺序
        self.flop = []                              # 翻牌圈牌面
        self.turn = []                              # 转牌圈牌面
        self.river = []                             # 河牌圈牌面

        self.first_round_judge = True               # 首轮叫牌顺序bool

    def init_cards(self):
        '''
        牌初始化
        :return:
        '''
        numlist = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        # flowers = ['♠', '♥', '♦', '♣']
        flowers = ['spade', 'heart', 'club', 'diamond']
        for i in numlist:
            for j in flowers:
                self.carddic[i + j] = ''
                self.cardlist.append(i + j)

    def add_player(self, player):
        '''
        添加玩家
        :param player: 新加入的player
        :return:
        '''
        self.playerlist.append(player)
        print('已加入新玩家，玩家姓名：', player.player_name, '玩家ip和端口号', player.id)
        print(self.playerlist)

    def show_off(self):
        for i in self.playerlist:
            if i.action != 'fold':
                print('玩家：' + i.player_name + '的牌面为' + str(i.cards))

    def start_round_call(self):
        for i in self.call_list:
            if self.playerlist[i].action != 'fold':
                print('轮到你了：', self.playerlist[i].player_name)
                self.last_chip = self.playerlist[i].get_action(self.last_chip)
                if self.if_last_player():
                    self.check_out()
                    return 0
        return 1

    def make_player_init(self):
        for i in self.playerlist:
            i.game_init()

    def get_max_chip(self):
        return max([self.playerlist[i].now_chip for i in range(0, len(self.playerlist))])

    def get_status_info(self):
        return [(i.id, i.player_name, i.act, i.now_chip, i.chip, i.action) for i in self.playerlist]

    def get_call_list(self):
        if self.first_round_judge:
            call_list = [i for i in range(self.bb_index + 1, len(self.playerlist))]
            for i in range(0, self.bb_index + 1):
                call_list.append(i)
            self.call_list = call_list
            self.first_round_judge = False
        else:
            call_list = [i for i in range(self.sb_index, len(self.playerlist))]
            for i in range(0, self.sb_index):
                call_list.append(i)
            self.call_list = call_list

    def choose_act(self):
        self.banker_index = 0 if self.banker_index == len(self.playerlist) else self.banker_index + 1
        self.sb_index = 0 if self.sb_index + 1 == len(self.playerlist) else self.sb_index + 1
        self.bb_index = 0 if self.bb_index + 1 == len(self.playerlist) else self.bb_index + 1
        self.playerlist[self.banker_index].get_act('bk', 0)
        print('庄家为：', self.playerlist[self.banker_index].player_name)
        self.playerlist[self.sb_index].get_act('sb', self.min_chip)
        print('小盲为：', self.playerlist[self.sb_index].player_name)
        self.playerlist[self.bb_index].get_act('bb', self.min_chip * 2)
        print('大盲为：', self.playerlist[self.bb_index].player_name)
        other_player_index = set(range(0, len(self.playerlist))) - set([self.banker_index]) - set([self.sb_index]) - set([self.bb_index])
        for index in other_player_index:
            self.playerlist[index].get_act('', 0)

    def check_out(self):
        name = ''
        for i in self.playerlist:
            if i.action != 'fold':
                print('游戏结束，赢家为：', i.player_name)
                name = i.player_name
                max_chip = i.now_chip
        sum_chip = 0
        for i in self.playerlist:
            if i.player_name != name:
                sum_chip += i.now_chip if i.now_chip <= max_chip else max_chip
                loss_chip = i.now_chip if i.now_chip <= max_chip else max_chip
                i.now_chip -= i.now_chip if i.now_chip <= max_chip else max_chip
                i.check_out(i.now_chip)
                print('玩家结算，', i.player_name, '-' + str(loss_chip))
        for i in self.playerlist:
            if i.player_name == name:
                sum_chip += i.now_chip
                i.check_out(sum_chip)
                print('玩家结算，', i.player_name, sum_chip)
        for i in self.playerlist:
            i.now_chip = 0
            print(i.player_name, '当前筹码:', i.chip)
        return name

    def check_out2(self):
        id = input('请输入赢家id：')
        for i in self.playerlist:
            if i.id == id:
                print('游戏结束，赢家为：', i.player_name)
                max_chip = i.now_chip
        sum_chip = 0
        for i in self.playerlist:
            if i.id != id:
                sum_chip += i.now_chip if i.now_chip <= max_chip else max_chip
                loss_chip = i.now_chip if i.now_chip <= max_chip else max_chip
                i.now_chip -= i.now_chip if i.now_chip <= max_chip else max_chip
                i.check_out(i.now_chip)
                print('玩家结算，', i.player_name, '-' + str(loss_chip))
        for i in self.playerlist:
            if i.id == id:
                sum_chip += i.now_chip
                i.check_out(sum_chip)
                print('玩家结算，', i.player_name, sum_chip)
        for i in self.playerlist:
            print(i.player_name, '当前筹码:', i.chip)

    def if_last_player(self):
        fold_cnt = 0
        for i in self.playerlist:
            fold_cnt = fold_cnt + 1 if i.action == 'fold' else fold_cnt
        if fold_cnt == len(self.playerlist) - 1:
            return True
        else:
            return False

    def get_random_card(self):
        '''
        随机卡
        :return:
        '''
        randindex = random.randint(0, len(self.cardlist) - 1)
        while self.carddic[self.cardlist[randindex]] != '':
            randindex = random.randint(0, len(self.cardlist) - 1)
        self.carddic[self.cardlist[randindex]] = -1
        return self.cardlist[randindex]

    def send_cards(self):
        '''
        开局发牌
        :param player_num: the number of players
        :return:
        '''
        card_list = []
        for i in self.playerlist:
            tmpcards = [self.get_random_card(), self.get_random_card()]
            card_list.append(tmpcards)
            i.get_cards(tmpcards)

    def send_flop(self):
        self.flop = [self.get_random_card(), self.get_random_card(), self.get_random_card()]
        print('翻牌圈：', self.flop)

    def send_turn(self):
        self.turn = [self.get_random_card()]
        print('转牌圈：', self.turn)

    def send_river(self):
        self.river = [self.get_random_card()]
        print('河牌圈：', self.river)

    def if_thesame_chip(self):
        tmplist = [i.now_chip for i in self.playerlist if i.action != 'fold']
        if max(tmplist) == min(tmplist):
            return True
        else:
            return False

    def get_all_user(self):
        print('各玩家的位置情况：', [(i.player_name, i.id, i.act) for i in self.playerlist])
