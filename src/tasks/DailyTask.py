import re
import time

from qfluentwidgets import FluentIcon

from src.tasks.ErBaseTask import ErBaseTask, name_re


class DailyTask(ErBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "清日常任务"
        self.description = "每个活动必须有预设阵容, 预设阵容必须能赢"
        self.icon = FluentIcon.SYNC
        self.default_config.update({
            '下拉菜单选项': "第一",
            '是否选项默认支持': False,
            'int选项': 1,
            '文字框选项': "默认文字",
            '长文字框选项': "默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字默认文字",
            'list选项': ['第一', '第二', '第3'],
        })
        self.config_type["下拉菜单选项"] = {'type': "drop_down",
                                      'options': ['第一', '第二', '第3']}

    def run(self):
        self.log_info('日常任务开始运行!', notify=True)
        self.xiehui()
        self.huanyin()
        self.challenge_activity('暗笼激斗',True)
        self.log_info('一键日常完成!', notify=True)

    def xiehui(self):
        self.go_to_menu('超链协会')
        self.wait_click_ocr(match='签到', box='bottom_left', after_sleep=0.5, raise_if_not_found=True)
        if not self.wait_click_ocr(match=re.compile('点击空白处'), raise_if_not_found=False, time_out=1.5):
            self.back(after_sleep=1)
        self.wait_click_ocr(match='锚点勘测', box='top_right', after_sleep=2, raise_if_not_found=True)
        if not self.ocr(match=[re.compile('sss', re.IGNORECASE), '100'], box='bottom_left'):
            self.log_info('协会boss, 未达到sss, 进入战斗')
            self.battle()

    def huanyin(self, go_to=True):
        if go_to and not self.go_to_challenge('试炼挑战','幻音剧场', check_not_challenged=True):
            self.log_info('已经挑战')
            return False
        self.wait_click_ocr(box='bottom_right', match='匹配', after_sleep=1)
        self.wait_ocr(box='bottom_right', match='开始', raise_if_not_found=True, time_out=60)
        self.log_info('wait 开始 success')
        self.sleep(3)
        chars = self.wait_ocr(0.26,0.91, 0.74,0.98, match=name_re, raise_if_not_found=True, time_out=10)
        self.log_info('wait chars success')
        self.sleep(1)
        for char in chars:
           self.click(char, after_sleep=0.5)
           self.log_info(f'click char {char} success')
        self.log_info('点击上阵角色完成')
        start_time = time.time()
        while time.time() - start_time < 60:
            if click:= self.ocr(box='bottom_right', match='开始'):
               self.click(click, after_sleep=1)
            elif self.ocr(box='bottom_right', match='匹配'):
                self.huanyin(go_to=False)
            else:
                break
        self.wait_click_ocr(0.74,0.44,0.80,0.49, match='是', time_out=180, raise_if_not_found=True)
        self.ensure_main()






