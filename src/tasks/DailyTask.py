import re
import time

from qfluentwidgets import FluentIcon

from src.tasks.ErBaseTask import ErBaseTask, name_re
from src.tasks.FarmTask import FarmTask


class DailyTask(FarmTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "一键收菜"
        self.description = "每个活动必须有预设阵容, 预设阵容必须能赢"
        self.icon = FluentIcon.SYNC
        self.default_config.update({
            '协会祈愿': ''
        })
        self.config_description.update({
            '协会祈愿': "自动发布和领取祈愿, 输入完整名字, 必须在第一页, 不输入则不祈愿",
        })

    def run(self):
        self.log_info('日常任务开始运行!', notify=True)
        self.activity_haiying()
        self.activity_huanfang()
        self.huanyin()
        self.challenge_activity('暗笼激斗', True)
        self.xiehui()
        self.farm()
        self.go_to_menu('任务')
        self.log_info('一键日常完成!', notify=True)

    def activity_huanfang(self):
        if self.go_to_challenge(name='幻方奇缘', index='限时活动', check_not_challenged=True):
            self.wait_ocr(match='幻方奇缘', settle_time=1, raise_if_not_found=True)
            self.click(0.9, 0.83, after_sleep=1)
            if not self.wait_ocr(match='发牌结束', settle_time=1):
                raise Exception('请先发牌完成再开始!')
            x = 0.15
            step_x = 0.044
            step_y = 0.097
            for i in range(6):
                y = 0.35
                for j in range(5):
                    self.click(x, y, after_sleep=1)
                    if self.ocr(match='开始战斗'):
                        self.battle()
                        self.wait_ocr(match='发牌结束')
                    y += step_y
                x += step_x

    def activity_haiying(self):
        if self.go_to_challenge(name='骇影迷踪', index='限时活动', check_not_challenged=True):
            self.wait_click_ocr(match=re.compile('今日剩余次数'), settle_time=1, raise_if_not_found=False)
            self.sleep(3)
            while True:
                texts = self.ocr(box='top')
                self.click(0.5, 0.5, after_sleep=0.5)
                for text in texts:
                    self.click(text, after_sleep=0.5)
                    if "需求" in text.name and '好友' not in text.name and '协会' not in text.name:
                        break
                self.wait_click_ocr(match=re.compile('挑战'), settle_time=1, raise_if_not_found=True)
                self.battle(click_enter=False)
                for i in range(4):
                    self.click(0.5, 0.24, after_sleep=1)
                if self.ocr(match=re.compile('今日剩余次数')):
                    break

    def xiehui(self):
        self.go_to_menu('超链协会')
        self.wait_click_ocr(match='签到', box='bottom_left', after_sleep=0.5, raise_if_not_found=True)
        if not self.wait_click_ocr(match=re.compile('点击空白处'), raise_if_not_found=False, time_out=1.5,
                                   after_sleep=2):
            self.back(after_sleep=1)
        if hero := self.config.get('协会祈愿'):
            self.wait_click_ocr(box='bottom_right', match='协会共助', raise_if_not_found=True, after_sleep=3)
            if claim := self.ocr(box='top_left', match=re.compile('可领取')):
                self.click(claim, after_sleep=1)
                self.handle_click_empty(time_out=3)
            fabu = self.ocr(box='top_left', match=re.compile('点击发布'))
            if fabu:
                self.click(fabu, after_sleep=1)
                if self.wait_click_ocr(box='left', match=hero, raise_if_not_found=True, settle_time=1, after_sleep=1):
                    self.wait_click_ocr(box='bottom_left', match='确认祈愿', raise_if_not_found=True, after_sleep=2)
                    self.click(fabu, after_sleep=1)
                    self.wait_click_ocr(match='确定', after_sleep=1, raise_if_not_found=True)
                    self.handle_click_empty(time_out=5)
                    self.back(after_sleep=1)
            else:
                self.back(after_sleep=1)
        self.wait_click_ocr(match='锚点勘测', box='top_right', after_sleep=3, raise_if_not_found=True)
        self.handle_click_empty(time_out=2)
        self.log_info('开始检查是否打过协会战')
        if not self.ocr(match=[re.compile('sss', re.IGNORECASE), '100'], box='bottom_left'):
            self.log_info('协会boss, 未达到sss, 进入战斗')
            self.battle()
        else:
            self.log_info('已经打过协会战')

    def huanyin(self, go_to=True):
        if go_to and not self.go_to_challenge('试炼挑战', '幻音剧场', check_not_challenged=True):
            self.log_info('已经挑战')
            return False
        while self.wait_click_ocr(box='bottom_right', match='匹配', after_sleep=1):
            self.wait_ocr(box='bottom_right', match='开始', raise_if_not_found=False, time_out=60)
        self.log_info('wait 开始 success')
        self.sleep(3)
        self.click_chars()
        self.log_info('点击上阵角色完成')
        start_time = time.time()
        while time.time() - start_time < 60:
            if click := self.ocr(box='bottom_right', match='开始'):
                self.click(click, after_sleep=1)
            elif self.ocr(box='bottom_right', match='匹配'):
                self.huanyin(go_to=False)
            else:
                break
        self.wait_click_ocr(0.74, 0.44, 0.80, 0.49, match='是', time_out=180, raise_if_not_found=True)
        self.ensure_main()
