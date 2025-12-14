from src.tasks.ErBaseTask import ErBaseTask


class AutoRestartFarmTask(ErBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "自动再来一次"
        self.description = "需要在能显示完成按钮的界面开始, 自动点击挂机的完成, 并且根据配置使用体力"
        self.default_config.update({
            '使用体力药': False,
        })

    def run(self):
        self.go_to_challenge()
        self.auto_restart()
