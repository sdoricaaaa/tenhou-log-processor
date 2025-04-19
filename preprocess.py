import json
import pandas as pd

from rule import Tiles, Player


def read_log(path):
    log_file = open(path, 'rt')
    raw_json = json.loads(log_file.read())
    log_file.close()
    return raw_json

def parse_json(data):
    ref = data['ref']
    dan = data['dan']
    rate = data['rate']
    name = data['name']
    rule = data['rule']
    log = data['log']

    player0 = Player(0, name[0], dan[0], rate[0])
    player1 = Player(1, name[1], dan[1], rate[1])
    player2 = Player(2, name[2], dan[2], rate[2])
    player3 = Player(3, name[3], dan[3], rate[3])

    res = [parse_one_round(i, [player0, player1, player2, player3]) for i in log]

    return [ref, rule, res]

def parse_one_round(round_log, player_list):
    # define round controller, pre-read data
    round_info = round_log[0] # 场次信息
    init_score = round_log[1] # 本场玩家点数
    bonus_indicators_queue = round_log[2] # 本场宝牌指示牌队列 (仅表宝牌)
    turn_num = 0 # 当前巡目
    current_bonus_indicators = [bonus_indicators_queue[0]] # 已揭示的宝牌指示牌
    round_wind = Tiles.winds_t34_idx_list[round_info[0]] # 场风牌



    round_result = round_log[16] # 本场结果详细信息
    turn_detail = [list] # 每巡的详细信息



    # set player info
    for player in player_list:
        player.set_init_info(round_log[player.idx * 3 + 0 + 4], round_log[player.idx * 3 + 1 + 4],
                             round_log[player.idx * 3 + 2 + 4], init_score[player.idx], round_info[1])
        player.riichi = False

    # init actions
    next_drawing_actions = [player_list[i].drawing_action_queue.pop() for i in range(4)]
    next_discard_actions = [player_list[i].discard_action_queue.pop() for i in range(4)]

    current_player_idx = round_info[1]
    # start round deduction
    while player_list[current_player_idx].drawing_action_queue: # loop for every player in one turn

        # # 每当一个玩家行动前，预读取一巡内玩家行动，判断是否有吃，碰，杠等动作出现
        # action_player_idx = -1
        # for draw in next_drawing_actions:
        #     if not draw.isnumeric(): # 处理有动作的情况
        #         # 获取执行动作的玩家idx
        #         action_player_idx = next_drawing_actions.index(draw)
        #         # 确认目标玩家的idx，通过动作识别符出现的的位置确定
        #         target_player_idx = -1
        #         for action in ['c', 'p', 'm']:
        #             if draw.find(action) is not -1:
        #                 target_player = draw.find(action) / 2 # 预期值包含0，1，2，3，其中0代表上家，1，代表对家，2，3代表下家
        #                 if target_player == 3:
        #                     target_player = 2
        #                 target_player_idx = action_player_idx - target_player - 1
        #                 break
        #         # TODO 获取到目标玩家的idx之后，当这个玩家弃牌后，直接切换到执行动作的玩家
        #         break
        #
        #
        # current_action = next_drawing_actions[current_player_idx]
        # next_drawing_actions[current_player_idx] = player_list[current_player_idx].drawing_action_queue.pop()
        current_action = player_list[current_player_idx].drawing_action_queue.pop()

        # handle different draw action
        if current_action.isnumeric(): # 正常抽牌
            # todo: 输出完整日志，后续根据模型需要再处理数据。 以字典格式暂存，后续转为Date Frame
            player_list[current_player_idx].hand.append(current_action)
            player_list[current_player_idx].counts[current_action] -= 1
        else: # 三种抽牌行为判断

            for action in Tiles.action_type: # TODO: 错误：碰牌应主动判断回合跳入，同时解决各种杠牌的回合跳入，可通过指定current_player的方式实现
                if action in current_action:
                    from_idx = current_action.index(action) // 2
                    meld = current_action.replace(action, '')
                    meld_list = [int(meld[i*2:(i+1)*2]) for i in range(len(meld) // 2)]
                    player_list[current_player_idx].meld.append(meld_list)
                    action_tile = meld.pop(from_idx)
                    for tile in meld_list:
                        player_list[current_player_idx].hand.remove(tile)
                    meld_json = {'type': Tiles.action_type.index(action) + 1, 'tiles': meld_list,
                                 'discarded_tile': action_tile, 'from': from_idx}
                    player_list[current_player_idx].meld_json_list.append(meld_json)
                    player_list[current_player_idx].meld.append(meld_list)
                    break

        # handle discard action
        if player_list[current_player_idx].discard_action_queue:
            current_discard = player_list[current_player_idx].discard_action_queue.pop()
        else:
            player_list[current_player_idx].discard_history.append(-1)
        if current_discard.isnumeric():
            if current_discard == 0:
                continue
                # TODO: check later!! 检查是否需要进行操作
            if current_discard == 60:
                current_discard = current_action
            player_list[current_player_idx].discard_history.append(current_discard)

        else:
            for action in Tiles.action_type:
                if action in current_discard:
                    meld = current_discard.replace(action, '')
                    meld_list = [int(meld[i * 2:(i + 1) * 2]) for i in range(len(meld) // 2)]
                    if len(meld_list) == 1: # riichi action
                        player_list[current_player_idx].riichi = True
                        player_list[current_player_idx].discard_history.append(meld)
                        break
                    elif action is 'k': # added kan, find meld in list
                        for i in player_list[current_player_idx].meld:
                            if meld_list[0] in i:
                                i.append(meld_list[0])
                                player_list[current_player_idx].hand.remove(meld_list[0])
                                for meld_json in player_list[current_player_idx].meld_json_list:
                                    if meld_json.get('type') is 1 and meld_list[0] in meld_json.get('tiles'):
                                        meld_json['type'] = Tiles.action_type.index(action) + 1
                                        meld_json['tiles'] = meld_list

                    # closed kan
                    else:
                        player_list[current_player_idx].meld.append(meld_list)
                        for tile in meld_list:
                            player_list[current_player_idx].hand.remove(tile)
                        meld_json = {'type': Tiles.action_type.index(action) + 1, 'tiles': meld_list,
                                     'discarded_tile': current_discard, 'from': current_player_idx}
                        player_list[current_player_idx].meld_json_list.append(meld_json)
                    turn_num += 1

        #check other three players' drawing action, if response this discard then change current_player_idx to the responser



def parse_round(round_log, player_list):
    # pre-read data
    _round_info = round_log[0]
    _init_score = round_log[1]
    _bonus_indicators_queue = round_log[2]
    _init_hands = [round_log[3 * i + 4] for i in [0,1,2,3]]
    _drawing_action_sequences = [round_log[3 * i + 5] for i in range(4)]
    _discard_action_sequences = [round_log[3 * i + 6] for i in range(4)]

    turn_num = 0
    current_bonus_indicators = [_bonus_indicators_queue[0]]

    # init state
    _next_drawing_actions = [_drawing_action_sequences[i][0] for i in range(4)]
    _next_discard_actions = [_discard_action_sequences[i][0] for i in range(4)]
