import re
import time

from qfluentwidgets import FluentIcon

from src.tasks.ErBaseTask import ErBaseTask, name_re


class FarmTask(ErBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "刷指定本, 直到没有体力"
        self.description = "每个活动必须有预设阵容, 预设阵容必须能赢, 不能开启锁定阵容"
        self.icon = FluentIcon.SYNC
        self.default_config.update({
            '刷什么': "多琪",
            '使用体力药': False,
            '买60钻体力': False,
            '买100钻体力': False,
        })
        self.yuanqi = ['兵祸', '多琪', '奥洛拉']
        self.zhiqiao = ['妮可娜娜', '莎朗', '赫妍', '炼狱津', '科洛罗']
        self.config_type["刷什么"] = {'type': "drop_down",
                                      'options': self.yuanqi + self.zhiqiao, }

    def run(self):
        self.log_info('日常任务开始运行!', notify=True)
        self.farm()

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
            self.sleep(0.5)
        else:
            for i in range(self.yuanqi.index(to_farm)):
                self.click(0.8, 0.50, down_time=0.001, after_sleep=2)
        self.ocr(log=True)
        # self.screenshot('farm')
        self.wait_click_ocr(match=re.compile(to_farm), raise_if_not_found=True, after_sleep=3)
        # self.click(0.55, 0.5, after_sleep=2)
        if self.continues_battle():
            self.auto_restart()
