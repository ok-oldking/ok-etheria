import re
import time

from qfluentwidgets import FluentIcon

from src.tasks.ErBaseTask import ErBaseTask, name_re


class AbyssTask(ErBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "墟烬探索(危机)"
        self.description = "必须已经通关, 从危机界面开始"
        self.icon = FluentIcon.SYNC

    def run(self):
        # self.go_to_challenge('试炼挑战', '深渊挑战')
        # self.wait_click_ocr(match='前往挑战', settle_time=0.5, after_sleep=5)
        # return self.battle()
        while True:
            if auto := self.ocr(match='自动挑战'):
                self.click(auto, after_sleep=2)
                self.handle_click_empty()
                self.sleep(1)
            self.wait_click_ocr(match='前往挑战', settle_time=0.5, after_sleep=5)
            self.battle_once()
            self.open_chest()

    def open_chest(self):
        self.send_key_down('w')
        self.wait_ocr(match='宝箱')
        self.send_key_up('w')
        self.sleep(2)
        self.send_key('f', after_sleep=3)
        self.handle_click_empty()
        self.sleep(1)
        self.send_key('d', down_time=0.2)
        self.sleep(1)
        self.send_key('w', down_time=0.2)
        self.sleep(1)
        self.send_key('a', down_time=0.2)
        self.sleep(1)
        self.sleep(2)
        self.send_key_down('w')
        start = time.time()
        while True:
            texts = self.ocr()
            if self.find_boxes(texts, match='开门'):
                self.send_key_up('w')
                self.sleep(1)
                self.send_key('f')
                self.sleep(8)
                self.send_key_down('w')
                start = time.time()
            if time.time() - start > 10:
                self.send_key('a', down_time=0.2, after_sleep=1)
            if self.find_boxes(texts, match='自动挑战'):
                break
            self.sleep(1)
        self.send_key_up('w')
        self.sleep(2)

    def battle_once(self):
        self.wait_ocr(match=[re.compile('击败'), '前往下一层'], settle_time=1)
        self.send_key_down('w')
        self.wait_ocr(match='进入战斗')
        self.send_key_up('w')
        self.sleep(2)
        self.click(0.25, 0.48, after_sleep=0.5)
        self.click(0.43, 0.48, after_sleep=0.5)
        self.click(0.59, 0.48, after_sleep=0.5)
        self.click(0.77, 0.48, after_sleep=1)
        self.battle(use_preset=False)
