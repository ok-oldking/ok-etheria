import re

from src.tasks.ErBaseTask import ErBaseTask


class AutoAlotTask(ErBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Task name: Automatic Blackjack, Source Web assistance, etc.
        self.name = "自动21点, 源网辅助点击等"

    def run(self):
        # Using a mix of regex objects and strings for flexible matching
        match_patterns = [
            '异常排除',
            '前往挑战',
            '再来一局',
            re.compile(r'点击空白处'),
            '匹配',
            '点击领取',
            '确认',
        ]

        self.logger.info(f"开始执行任务: {self.name}")

        while True:  # Using a flag is safer than 'True' for stopping tasks
            # Perform OCR to find text elements on screen
            results = self.ocr()

            if results:
                for target in match_patterns:
                    # Find if the target exists in the OCR results
                    # Assuming self.ocr() returns objects with .text and .center properties
                    found_node = self.find_text(results, target)

                    if found_node:
                        self.logger.info(f"检测到目标: {target}, 执行点击")
                        self.click(found_node)
                        # Break after a click to allow the UI to refresh
                        self.sleep(0.5)
                        break

            self.sleep(1)

    def find_text(self, results, target):
        """
        Helper to match either a regex pattern or a substring/exact string.
        """
        for node in results:
            text = node.name
            if isinstance(target, re.Pattern):
                if target.search(text):
                    return node
            elif target in text:
                return node
        return None