class Tiles:


    t60_idx_list = [11, 12, 13, 14, 15, 16, 17, 18, 19,
                    21, 22, 23, 24, 25, 26, 27, 28, 29,
                    31, 32, 33, 34, 35, 36, 37, 38, 39,
                    41, 42, 43, 44, 45, 46, 47,
                    51, 52, 53]

    tile_type_list = ['manzu', 'pinzu', 'sozu', 'wind', 'dragon']

    tile_name_list = ['1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
            '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
            '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
            '1z', '2z', '3z', '4z', '5z', '6z', '7z',
            '0m', '0p', '0s']

    winds_t34_idx_list = [tile_name_list.index('1z'), tile_name_list.index('2z'),
                          tile_name_list.index('3z'), tile_name_list.index('4z')]

    action_type = ['p', 'c', 'a', 'm', 'k', 'r'] # Pon, Chii, close Kan, open Kan, added Kan, riichi
    '''
    "pon, chii, open kan" are considered as "drawing actions", "close kan, added kan" are treated as "discard actions"
    in open kan, discard will show 0 for marking up. and then jump to drawing tile.
    '''
    drawing_action = ['p', 'c', 'm']
    discard_action = ['a', 'k', 'r']


    def __init__(self, idx):
        if idx > 36 or idx < 0:
            raise ValueError('Index out of range')

        self.idx = idx
        self.name = self.tile_name_list[idx]
        self.redBonus = idx > 33
        # define tile_type
        if 26 < idx < 34:
            if idx > 30:
                self.type = 'wind'
            else:
                self.type = 'dragon'
        elif idx > 17 or idx == 36:
            self.type = 'sozu'
        elif idx > 8 or idx == 35:
            self.type = 'pinzu'
        elif idx >= 0 or idx == 34:
            self.type = 'manzu'


    def __str__(self):
        return self.name

class Player:

    def __init__(self, idx, name, dan, rate):
        self.self_wind = None
        self.score = 25000
        self.idx = idx
        self.riichi = False
        self.tenpai = False
        self.name = name
        self.dan = dan
        self.rate = rate
        self.hand = [int]
        self.meld = [list[int]]
        self.meld_json_list = []
        self.counts = [4] * 34 + [1] * 3

        self.counts[4] = 3 # remove red bonus count
        self.counts[4 + 1 * 9] = 3
        self.counts[4 + 2 * 9] = 3

        self.drawing_action_queue = []
        self.discard_action_queue = []
        self.discard_history = [int]

    def set_init_info(self, hand, action_queue, discard_queue, score, round_num):
        self.hand = hand
        self.drawing_action_queue = action_queue
        self.discard_action_queue = discard_queue
        self.discard_history = []
        for num in hand:
            self.counts[num] -= 1
        self.score = score
        self.self_wind = Tiles.winds_t34_idx_list[self.idx - round_num]

    def add_new_discard(self, new_discard):
        self.discard_history.append(new_discard)
