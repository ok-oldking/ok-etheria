# Test case
import unittest

from src.config import config
from ok.test.TaskTestCase import TaskTestCase

from src.tasks.DailyTask import DailyTask


class TestMyOneTimeTask(TaskTestCase):
    task_class = DailyTask

    config = config

    def test_main2(self):
        self.set_image('tests/images/main2.png')
        is_main = self.task.find_chat()
        self.assertTrue(is_main)


if __name__ == '__main__':
    unittest.main()
