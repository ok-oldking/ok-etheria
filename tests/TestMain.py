# Test case
import unittest

from src.config import config
from ok.test.TaskTestCase import TaskTestCase

from src.tasks.DailyTask import DailyTask


class TestMyOneTimeTask(TaskTestCase):
    task_class = DailyTask

    config = config

    def test_ocr1(self):
        # Create a BattleReport object
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
