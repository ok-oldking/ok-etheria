import os

version = "dev"

config = {
    'debug': False,  # Optional, default: False
    'use_gui': True,  # 目前只支持True
    'config_folder': 'configs',  # 最好不要修改
    'gui_icon': 'icons/icon.png',  # 窗口图标, 最好不需要修改文件名
    'wait_until_before_delay': 0,
    'wait_until_check_delay': 0,
    'wait_until_settle_time': 0,  # 调用 wait_until时候, 在第一次满足条件的时候, 会等待再次检测, 以避免某些滑动动画没到预定位置就在动画路径中被检测到
    'ocr': {  # 可选, 使用的OCR库
        'lib': 'onnxocr',
        'params': {
            'use_openvino': True,
        }
    },
    'template_matching': {  # 可选, 如使用OpenCV的模板匹配
        'coco_feature_json': os.path.join('assets', 'result.json'),
        # coco格式标记, 需要png图片, 在debug模式运行后, 会对进行切图仅保留被标记部分以减少图片大小
        'default_horizontal_variance': 0.002,  # 默认x偏移, 查找不传box的时候, 会根据coco坐标, match偏移box内的
        'default_vertical_variance': 0.002,  # 默认y偏移
        'default_threshold': 0.8,  # 默认threshold
    },
    'windows': {  # Windows游戏请填写此设置
        'exe': ['GameUE_cpp-Win64-Shipping.exe'],
        'calculate_pc_exe_path': 'taptap://taptap.com/app?app_id=236627&platform=pc&auto_launch=true&ch_src=desktop---',
        # 'hwnd_class': 'UnrealWindow', #增加重名检查准确度
        'interaction': 'PostMessage',
        # Genshin:某些操作可以后台, 部分游戏支持 PostMessage:可后台点击, 极少游戏支持 ForegroundPostMessage:前台使用PostMessage Pynput/PyDirect:仅支持前台使用
        'capture_method': ['WGC', 'BitBlt_RenderFull'],
        # Windows版本支持的话, 优先使用WGC, 否则使用BitBlt_Full. 支持的capture有 BitBlt, WGC, BitBlt_RenderFull, DXGI
        'check_hdr': True,  # 当用户开启AutoHDR时候提示用户, 但不禁止使用
        'force_no_hdr': False,  # True=当用户开启AutoHDR时候禁止使用
        'require_bg': True  # 要求使用后台截图
    },
    'start_timeout': 120,  # default 60
    'window_size': {  # ok-script窗口大小
        'width': 1200,
        'height': 800,
        'min_width': 600,
        'min_height': 450,
    },
    'supported_resolution': {
        'ratio': '16:9',  # 支持的游戏分辨率
        'min_size': (1280, 720),  # 支持的最低游戏分辨率
        'resize_to': [(2560, 1440), (1920, 1080), (1600, 900), (1280, 720)],  # 可选, 如果非16:9自动缩放为 resize_to
    },
    'links': {  # 关于里显示的链接, 可选
        'default': {
            'github': 'https://github.com/ok-oldking/ok-etheria',
            'discord': 'https://discord.gg/vVyCatEBgA',
            'sponsor': 'https://www.paypal.com/ncp/payment/JWQBH7JZKNGCQ',
            'share': 'Download from https://github.com/ok-oldking/ok-etheria',
            'faq': 'https://github.com/ok-oldking/ok-etheria',
            'qq_group': 'https://qm.qq.com/q/vkOIHjakBW',
            'qq_channel': 'https://pd.qq.com/s/djmm6l44y',
        }
    },
    'screenshots_folder': "screenshots",  # 截图存放目录, 每次重新启动会清空目录
    'gui_title': 'ok-er',  # 窗口名
    'version': version,  # 版本
    'my_app': ['src.globals', 'Globals'],  # 可选. 全局单例对象, 可以存放加载的模型, 使用og.my_app调用
    'onetime_tasks': [  # 用户点击触发的任务
        ["src.tasks.DailyTask", "DailyTask"],
        ["src.tasks.FarmTask", "FarmTask"],
        ["src.tasks.AutoRtaTask", "AutoRtaTask"],
        ["src.tasks.AbyssTask", "AbyssTask"],
        ["src.tasks.AutoRestartFarmTask", "AutoRestartFarmTask"],
        ["ok", "DiagnosisTask"],
    ],
    # 'trigger_tasks':[ # 不断执行的触发式任务
    #     ["src.tasks.MyTriggerTask", "MyTriggerTask"],
    # ],
}
