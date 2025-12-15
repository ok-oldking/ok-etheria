import re
import time

from ok import BaseTask

name_re = re.compile('[a-zA-Z\u4e00-\u9fff]+')
stamina_re = re.compile(r"^\d+/\d+")


class ErBaseTask(BaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_double = None

    def ensure_main(self):
        return self.wait_until(self.is_main, time_out=30, raise_if_not_found=True)

    def is_main(self):
        texts = self.ocr()
        if self.find_boxes(texts, match=['请选择兑换道具', '游戏公告']):
            self.back(after_sleep=1)
            return False
        if continue_game := self.find_boxes(texts, [re.compile('点击空白处'), '点击领取']):
            self.click(continue_game, after_sleep=1)
            return False
        if self.find_boxes(texts, ['适龄提示', '每日签到']):
            self.click(0.5, 0.75, after_sleep=1)
            return False
        if self.find_boxes(texts, ['返回登录', '继续游戏']):
            self.back(after_sleep=1)
            return False
        if self.find_boxes(texts, ['自动', '手动'], boundary='top_right'):
            if not self.find_boxes(texts, match='退出战斗'):
                self.log_info('战斗中, 点击暂停退出')
                self.click(0.94, 0.05, after_sleep=1)
            self.log_info('退出战斗, 点击esc')
            self.back(after_sleep=1)
            self.wait_click_ocr(match='确定', box='bottom_right', after_sleep=2, raise_if_not_found=True)
            return False
        if self.find_boxes(texts, ['继续战斗', '退出战斗']):
            self.log_info('退出战斗, 点击esc')
            self.back(after_sleep=1)
            self.wait_click_ocr(match='确定', box='bottom_right', after_sleep=2, raise_if_not_found=True)
            return False
        if self.has_menu(texts):  # 右上菜单已经打开
            self.sleep(1)
            return self.ocr()
        chat_main_page = self.find_one('chat_main_page')
        if chat_main_page:  # 主页
            self.log_debug(f'找到chat_main_page, 主页 {chat_main_page}')
            self.send_key('tab', after_sleep=1)
            return False
        else:
            self.back(after_sleep=1)
            return False

    def has_menu(self, texts):
        if not texts:
            texts = self.ocr()
        boxes = self.find_boxes(texts, match=['任务', '商店', '背包'], boundary='top_right')
        self.log_debug('check has_menu: {}'.format(boxes))
        return len(boxes) >= 3

    def is_challenge(self, texts=None):
        if not texts:
            texts = self.ocr()
        boxes = self.find_boxes(texts, match=['日常挑战', '试炼挑战', '限时活动'], boundary='top_left')
        is_challenge = len(boxes) >= 3
        self.log_debug('check is_challenge: {}'.format(boxes))
        if is_challenge and self.is_double is None:
            self.click(self.find_boxes(texts, match=['日常挑战'], boundary='top_left'), after_sleep=1)
            self.is_double = self.find_one('x2')
            self.log_info(f'is_double: {self.is_double}')
        return is_challenge

    def claim_quest(self):
        self.go_to_menu('任务')
        if claim := self.ocr(box='bottom_right', match='全部领取'):
            self.click(claim, after_sleep=1)
        while claim := self.ocr(box='bottom_left', match='领取'):
            self.click(claim, after_sleep=1)
            self.handle_click_empty()

    def click(self, *args, **kwargs):
        kwargs['down_time'] = 0.0001
        kwargs['move'] = True
        super().click(*args, **kwargs)

    def go_to_menu(self, name):
        texts = self.ensure_main()
        click = self.find_boxes(texts, match=name)
        self.click(click, after_sleep=2)
        self.log_info('打开菜单成功! {}'.format(name))

    def go_to_challenge(self, index='日常挑战', name=None, check_not_challenged=False):
        texts = self.ocr()
        if not self.is_challenge(texts):
            self.log_info('不在挑战界面, 去挑战界面')
            self.go_to_menu('挑战')
        if index:
            self.wait_click_ocr(match=index, box='left', after_sleep=2, raise_if_not_found=True)
        if name:
            texts = self.ocr()
            to_click = self.find_boxes(texts, match=name)[0]
            self.log_info(f'go_to_challenge check name {name} {to_click} {check_not_challenged}')
            if check_not_challenged:
                boundary = to_click.copy(y_offset=-to_click.height)
                if not self.find_boxes(texts, match='今日未挑战', boundary=boundary):
                    self.log_info('今日未挑战 not found')
                    return False
            self.wait_click_ocr(match=name, after_sleep=2, raise_if_not_found=True)
            return True

    def challenge_activity(self, name, check_not_challenged=False):
        if self.go_to_challenge(name=name, index='限时活动', check_not_challenged=check_not_challenged):
            self.battle()

    def continues_battle(self):
        self.log_info('点击开始连续战斗')
        self.wait_click_ocr(box='bottom_right', match='连续战斗', after_sleep=1, raise_if_not_found=True)
        self.wait_click_ocr(match='开始战斗', after_sleep=1, raise_if_not_found=True)
        self.sleep(3)
        if self.ocr(match='开始战斗'):
            self.log_info('体力已用尽', notify=True)
            self.ensure_main()
            return False
        self.use_preset()
        self.click(0.95, 0.15, after_sleep=1)
        return True

    def auto_restart(self):
        while True:
            done = self.ocr(match="完成")
            if not done:
                self.log_info('没有找到完成, 检查领取任务')
                self.claim_quest()
                self.go_to_challenge()
                self.sleep(30)
                continue
            self.log_info('找到完成, 尝试使用体力药')
            self.use_stamina()
            self.log_info('点击完成')
            self.click(done, after_sleep=1)
            self.wait_click_ocr(box='bottom_right', match='再来一次', after_sleep=1, raise_if_not_found=True)
            if start := self.ocr(match='开始战斗'):
                self.click(start, after_sleep=3)
                if self.ocr(match='开始战斗'):
                    self.log_info('体力用尽, 结束', notify=True)
                    self.ensure_main()
                    break

    def use_preset(self):
        self.wait_click_ocr(box='bottom_right', match='预设', after_sleep=1, settle_time=0.5, raise_if_not_found=True)
        if not self.wait_click_ocr(box='left', match='使用', after_sleep=1, raise_if_not_found=False):
            raise Exception('没有预设阵容, 无法进行自动战斗!')
        self.wait_click_ocr(box='right', match='确定', after_sleep=1, raise_if_not_found=False, time_out=1)
        self.wait_click_ocr(box='bottom_right', match='战斗', after_sleep=1, raise_if_not_found=True)

    def battle(self):
        self.wait_click_ocr(box='bottom_right', match='前往挑战', after_sleep=1, settle_time=1, raise_if_not_found=True)
        self.use_preset()
        start = time.time()
        while time.time() - start < 800:
            texts = self.ocr()
            if manual := self.find_one('manual'):
                self.log_info('点击自动战斗')
                self.click(manual, after_sleep=3)
                continue
            if click := self.find_boxes(texts, re.compile('点击空白处')):
                self.log_info('战斗结束, 点击空白处关闭!')
                self.click(click, after_sleep=1)
                continue
            if self.find_boxes(texts, '前往挑战', 'bottom_right'):
                self.log_info('战斗结束!')
                self.sleep(1)
                break
            self.sleep(2)
            self.info_set('战斗时间', int(time.time() - start))
        self.log_info('战斗结束')

    def find_stamina(self):
        stamina_text = self.wait_ocr(box='top_right', match=stamina_re, raise_if_not_found=True)
        if stamina_text:
            current = int(stamina_text[0].name.split('/')[0])
            self.info_set(f'stamina', current)
            return current
        return -1

    def handle_click_empty(self, time_out=0.5):
        self.wait_click_ocr(box='bottom', match=re.compile('点击空白处'), time_out=time_out, after_sleep=1,
                            raise_if_not_found=False)

    def use_stamina(self):
        if not self.config.get('使用体力药') or not self.config.get('买60钻体力') or self.config.get('买100钻体力'):
            self.log_info('没有设置买体力, 跳过购买体力')
            return
        stamina = self.find_stamina()
        if stamina < 0:
            raise Exception('找不到体力')
        use_count = 0
        if stamina < 100:
            if self.is_double:
                use_count = 2
            else:
                use_count = 1
        elif stamina < 200:
            if self.is_double:
                use_count = 1
        self.log_info('stamina use_count: {}'.format(use_count))
        if use_count > 0:
            self.click(0.57, 0.05, after_sleep=1)
            texts = self.ocr()
            if self.find_boxes(texts, match=re.compile('精神稳定剂数量不足')):
                self.back(after_sleep=1)
                self.log_info('已经买满体力')
                return
            if not self.config.get('使用体力药'):
                self.click(0.57, 0.42, after_sleep=1)
                self.log_info('点击使用钻')
            if self.find_boxes(texts, match=re.compile('花费精神稳定剂')) and self.config.get('使用体力药'):
                self.log_info('使用体力药')
                buy = True
            elif self.config.get('买100钻体力'):
                self.log_info('买100钻体力')
                buy = True
            elif self.config.get('买60钻体力') and self.find_boxes(texts, match=re.compile('花费60海')):
                buy = True
                use_count = 1
                self.log_info('买一次60钻体力')
            else:
                self.log_info('设置为不购买体力!')
                buy = False
            if buy:
                if use_count > 1:
                    self.log_info('点击增加体力药')
                    self.click(0.61, 0.57, after_sleep=1)
                self.click(0.5, 0.77, after_sleep=1)
                self.log_info('点击确定')
                self.click(0.51, 0.94, after_sleep=1)
                self.log_info('点击空白')

            else:
                self.log_info('没有体力药或者设置为不使用体力药')
                self.back(after_sleep=1)
