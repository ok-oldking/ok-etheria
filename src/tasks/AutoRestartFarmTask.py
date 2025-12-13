import re

from ok import TriggerTask

from src.tasks.ErBaseTask import ErBaseTask


class AutoRestartFarmTask(ErBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "自动再来一次"
        self.description = "需要在能显示完成按钮的界面开始, 自动点击挂机的完成, 并且根据配置使用体力"
        self.default_config.update({
            '是否双倍中': False,
            '使用体力药': False,
        })

    def run(self):
        self.go_to_challenge()
        while True:
            done = self.ocr(match="完成")
            if not done:
                self.log_info('没有找到完成 继续等待')
                self.sleep(3)
                continue
            self.log_info('找到完成, 尝试使用体力药')
            self.use_stamina()
            self.log_info('点击完成')
            self.click(done, after_sleep=1)
            self.wait_click_ocr(box='bottom_right',match='再来一次', after_sleep=1, raise_if_not_found=True)
            if start:=self.ocr(match='开始战斗'):
                self.click(start, after_sleep=3)
                if self.ocr(match='开始战斗'):
                    self.log_info('体力用尽, 结束', notify=True)
                    break








