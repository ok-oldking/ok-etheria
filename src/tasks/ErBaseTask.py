import re
import time

from ok import BaseTask

name_re = re.compile('[a-zA-Z\u4e00-\u9fff]+')
stamina_re = re.compile(r"^\d+/\d+")

class ErBaseTask(BaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def ensure_main(self):
        return self.wait_until(self.is_main, time_out=30, raise_if_not_found=True)

    def is_main(self):
        texts = self.ocr()
        if continue_game:=self.find_boxes(texts, [re.compile('点击空白处'), '点击领取']):
            self.click(continue_game, after_sleep=1)
            return False
        if self.find_boxes(texts, ['适龄提示', '每日签到']):
            self.click(0.5,0.75, after_sleep=1)
            return False
        if self.find_boxes(texts, ['返回登录', '继续游戏']):
            self.back(after_sleep=1)
            return False
        if self.find_boxes(texts, ['自动', '手动'], boundary='top_right'):
            if not self.find_boxes(texts, match='退出战斗'):
                self.click(0.94,0.05, after_sleep=1)
            self.log_info('退出战斗, 点击esc')
            self.back(after_sleep=1)
            self.wait_click_ocr(match='确定', box='bottom_right', after_sleep=2, raise_if_not_found=True)
            return False
        if self.find_boxes(texts, ['继续战斗', '退出战斗']):
            self.log_info('退出战斗, 点击esc')
            self.back(after_sleep=1)
            self.wait_click_ocr(match='确定', box='bottom_right', after_sleep=2, raise_if_not_found=True)
            return False
        if self.has_menu(texts):  # 右上菜单已经打开
            self.sleep(1)
            return self.ocr()
        match = self.find_boxes(texts, ['活动','超链之证','商店', stamina_re], boundary='top')
        self.log_debug('match: {}'.format(match))
        if len(match) >= 2:  # 主页
            self.log_debug('找到活动/商店, 主页')
            self.send_key('tab', after_sleep=1)
            return False
        else:
            self.back(after_sleep=1)
            return False

    def has_menu(self, texts):
        if not texts:
            texts = self.ocr()
        boxes = self.find_boxes(texts, match=['任务','商店','背包'], boundary='top_right')
        self.log_debug('check is_challenge: {}'.format(boxes))
        return len(boxes) >= 3

    def is_challenge(self, texts=None):
        if not texts:
            texts = self.ocr()
        boxes = self.find_boxes(texts, match=['主线','竞技之域','超链协会'])
        self.log_debug('check is_challenge: {}'.format(boxes))
        return len(boxes) >= 3

    def go_to_menu(self, name):
        texts = self.ensure_main()
        click = self.find_boxes(texts, match=name)
        self.click(click, after_sleep=2)

    def go_to_challenge(self, index='日常挑战', name=None, check_not_challenged=False):
        texts = self.ocr()
        if not self.is_challenge(texts):
            self.go_to_menu('挑战')
        if index:
            self.wait_click_ocr(match=index, box='left', after_sleep=1)
        if name:
            texts = self.ocr()
            to_click = self.find_boxes(texts, match=name)[0]
            self.log_info(f'go_to_challenge check name {name} {to_click} {check_not_challenged}')
            if check_not_challenged:
                boundary = to_click.copy(y_offset=-to_click.height)
                if not self.find_boxes(texts, match='今日未挑战', boundary=boundary):
                    self.log_info('今日未挑战 not found')
                    return False
            while True:
                texts = self.ocr()
                to_click = self.find_boxes(texts, match=name)[0]
                if to_click and self.is_challenge(texts):
                    self.click(to_click, after_sleep=1)
                else:
                    break
            return True

    def challenge_activity(self, name, check_not_challenged=False):
        if self.go_to_challenge(name=name, index='限时活动', check_not_challenged=check_not_challenged):
            self.battle()

    def battle(self):
        self.wait_click_ocr(box='bottom_right', match='前往挑战', after_sleep=1, raise_if_not_found=True)
        self.wait_click_ocr(box='bottom_right', match='预设', after_sleep=1, settle_time=0.5, raise_if_not_found=True)
        if not self.wait_click_ocr(box='left', match='使用', after_sleep=1, raise_if_not_found=False):
            raise Exception('没有预设阵容, 无法进行自动战斗!')
        self.wait_click_ocr(box='right', match='确定', after_sleep=1, raise_if_not_found=False, time_out=1)
        self.wait_click_ocr(box='bottom_right', match='战斗', after_sleep=1, raise_if_not_found=True)
        start = time.time()
        while time.time() - start < 800:
            texts = self.ocr()
            if click := self.find_boxes(texts, re.compile('点击空白处')):
                self.log_info('战斗结束, 点击空白处关闭!')
                self.click(click, after_sleep=1)
                continue
            if self.find_boxes(texts, '前往挑战', 'bottom_right'):
                self.log_info('战斗结束!')
                self.sleep(1)
                break
            self.sleep(2)
            self.info_set('战斗时间', int(time.time() - start))
        self.log_info('战斗结束')


    def find_stamina(self):
        stamina_text = self.ocr(box='top_right', match=stamina_re)
        if stamina_text:
            current = int(stamina_text[0].name.split('/')[0])
            self.info_set(f'stamina', current)
            return current
        return -1

    def use_stamina(self):
        if not self.config.get('使用体力药'):
            return
        stamina = self.find_stamina()
        if stamina < 0:
            raise Exception('找不到体力')
        use_count = 0
        if stamina < 100:
            if self.config.get('是否双倍中'):
                use_count = 2
            else:
                use_count = 1
        elif stamina < 200:
            if self.config.get('是否双倍中'):
                use_count = 1
        self.log_info('stamina use_count: {}'.format(use_count))
        if use_count > 0:
            self.click(0.57, 0.05, after_sleep=1)
            if self.ocr(match=re.compile('精神稳定剂')) and self.config.get('使用体力药'):
                if use_count > 1:
                    self.log_info('点击增加体力药')
                    self.click(0.61, 0.57, after_sleep=1)
                self.click(0.5, 0.77, after_sleep=1)
                self.log_info('点击确定')
                self.click(0.51, 0.94, after_sleep=1)
                self.log_info('点击空白')
            else:
                self.log_info('没有体力药或者设置为不使用体力药')
                self.back()









