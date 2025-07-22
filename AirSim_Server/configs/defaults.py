from yacs.config import CfgNode as CN

FRONT="forward-looking"
BOTTOM="downward-looking"

def get_default_config():
    cfg = CN()

    # 默认相机视角
    cfg.view = FRONT
    # 默认文件存储路径
    cfg.cache = "cache"

    # 默认颜色文件路径，根据实际情况修改
    cfg.color_file = "configs/seg_rgbs.txt"

    # 无人机初始化位置与姿态
    cfg.init_pose = CN()
    cfg.init_pose.position = [500, 2100, -50]
    cfg.init_pose.orientation = [0, 0, 0, 1]  # 四元数表示

    # 货船和火灾建筑的object_id
    cfg.ship_id = 10

    # 无人机控制参数
    cfg.control = CN()
    # 移动
    cfg.control.base_speed = 5.0  # 基础速度
    cfg.control.step_dist = 20.0  # 每次移动距离
    cfg.control.move_step = 4  # 飞行步长时间

    # 转向
    cfg.control.yaw_rate = 30.0  # Yaw速度
    cfg.control.rotate_step = 3  # 转向步长时间

    # 长距离飞行
    cfg.control.cruise_velocity = 100.0  # 巡航飞行速度
    cfg.control.cruise_altitude = -120.0  # 巡航飞行高度

    # 任务参数
    cfg.task = CN()

    cfg.sleep_time = 10

    # 任务最大允许执行步数
    cfg.task.max_steps = 50

    # 任务判定
    # 判断货船是否在视野中的像素比例阈值
    cfg.task.ship_visible_threshold = 0.015

    # 判断火灾建筑是否在视野中的像素数量阈值
    cfg.task.building_visible_threshold = 10000

    # 判断火灾建筑是否被扑灭的像素数量阈值
    cfg.task.fire_extinguished_threshold = 500

    # 服务器相关参数
    cfg.server = CN()
    # 文件服务器端口
    cfg.server.file_port = 18080
    # airsim控制端口
    cfg.server.airsim_port = 28080
    # websockets端口
    cfg.server.ws_port = 38080

    cfg.agent = CN()
    cfg.agent.model_name = "ollama__qwen2.5vl:7b"
    cfg.agent.api_key = ""
    cfg.agent.max_tokens = 300

    return cfg.clone()

if __name__ == "__main__":
    cfg = get_default_config()
    print(cfg)
    
