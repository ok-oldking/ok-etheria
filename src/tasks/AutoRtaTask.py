import re
import time

from qfluentwidgets import FluentIcon

from src.tasks.ErBaseTask import ErBaseTask, name_re


class AutoRtaTask(ErBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "自动RTA, 大概率输, 完成任务用"
        self.description = ""
        self.icon = FluentIcon.SYNC
        self.default_config.update({
            '刷多少次': 20,
        })

    def run(self):
        self.go_to_menu('竞技之域')
        self.wait_click_ocr(match='巅峰竞技场', raise_if_not_found=True, settle_time=1)

        for i in range(self.config.get('刷多少次')):
            ended = False
            self.wait_click_ocr(match='匹配', raise_if_not_found=True, settle_time=1)
            self.wait_click_ocr(match='最近', raise_if_not_found=True, settle_time=1, time_out=300, after_sleep=1)
            self.wait_click_ocr(match='确认设置', after_sleep=1)
            self.wait_ocr(match=['对方回合', '确认选择'], time_out=60)
            while True:
                texts = self.ocr()
                if end := self.find_boxes(texts, match=['战斗成功', '战斗失败', re.compile('段位降低'),
                                                        re.compile('段位提升')]):
                    self.click(end, after_sleep=1)
                    if not ended:
                        self.info_incr(end[0].name)
                        ended = True
                    continue
                if self.find_boxes(texts, match=['匹配'], boundary='bottom_right'):
                    break
                if self.find_boxes(texts, match='对方回合'):
                    self.sleep(1)
                    continue
                if confirm := self.find_boxes(texts, match=['确认选择', '确认禁用']):
                    self.click_chars()
                    self.click(confirm, after_sleep=2)
                if manual := self.find_one('manual'):
                    self.log_info('点击自动战斗')
                    self.click(manual, after_sleep=3)
                    continue
                self.sleep(1)

    def farm(self):
        to_farm = self.config.get('刷什么')
        if to_farm in self.yuanqi:
            go_to = '熔断禁区'
        else:
            go_to = '凶影追缉'
        self.go_to_challenge(name=go_to)
        self.use_stamina()
        if go_to == '凶影追缉':
            self.scroll_relative(0.5, 0.5, -50)
            self.sleep(0.5)
            self.scroll_relative(0.5, 0.5, -50)
            self.sleep(2)
        else:
            for i in range(self.yuanqi.index(to_farm)):
                self.click(0.8, 0.50, down_time=0.001, after_sleep=2)
        self.ocr(log=True)
        # self.screenshot('farm')
        self.wait_click_ocr(match=re.compile(to_farm), settle_time=0.5, raise_if_not_found=True, after_sleep=3)
        # self.click(0.55, 0.5, after_sleep=2)
        if self.continues_battle():
            self.auto_restart()
