# -*- coding: utf-8 -*-
r"""仿真看鸭 —— 在 MuJoCo 里看 Microduck、掰关节、切姿势。

用法（在工作区根目录下）：
    .venv-sim\Scripts\python 仿真看鸭.py            # 打开 3D 查看器
    .venv-sim\Scripts\python 仿真看鸭.py --check    # 不开界面，只自检模型+打印对照表

查看器操作：
    鼠标左键拖      旋转视角
    滚轮 / 右键拖   缩放
    1 / 2 / 3 / 4   切换姿势：1=INIT(零位)  2=STAND(站)  3=SIT(坐)  4=FOLD(缩成一团)
    左侧面板 Joints 可以拖滑块单独掰每个关节 —— 对应真机上那颗舵机的角度
"""
import sys, os
import mujoco  # 顶层导入：joint_table 等函数也要用

SCENE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'microduck_rl', 'src', 'mjlab_microduck',
                     'robot', 'microduck', 'scene_walk.xml')

# 仿真关节名 -> (舵机 ID, 中文名)。ID 表来自 microduck-replica/调试记录.md（上游 model.rs 实测）。
# 注意：真机第 15 颗舵机「嘴 ID 34」不在步行仿真里 —— 走路用不上嘴。
JOINT_INFO = {
    'left_hip_yaw':   (20, '左髋 yaw（左右转腿根）'),
    'left_hip_roll':  (21, '左髋 roll（侧向摆腿）'),
    'left_hip_pitch': (22, '左髋 pitch（前后抬腿）'),
    'left_knee':      (23, '左膝'),
    'left_ankle':     (24, '左踝'),
    'neck_pitch':     (30, '颈俯仰（点头）'),
    'head_pitch':     (31, '头俯仰'),
    'head_yaw':       (32, '头 yaw（摇头）'),
    'head_roll':      (33, '头 roll（歪头）'),
    'right_hip_yaw':  (10, '右髋 yaw'),
    'right_hip_roll': (11, '右髋 roll'),
    'right_hip_pitch':(12, '右髋 pitch'),
    'right_knee':     (13, '右膝'),
    'right_ankle':    (14, '右踝'),
}

KEYFRAMES = ['INIT', 'STAND', 'SIT', 'FOLD']


def joint_table(model):
    lines = []
    lines.append(f"{'#':>2}  {'仿真关节名':<16} {'ID':>3}  {'中文名':<14} {'行程(°)':<14}")
    lines.append('-' * 62)
    for j in range(model.njnt):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j)
        if name is None:
            continue  # 跳过 free joint（机身浮动自由度，不是舵机）
        jtype = model.jnt_type[j]
        if jtype != mujoco.mjtJoint.mjJNT_HINGE:
            continue
        qadr = model.jnt_qposadr[j]
        lo, hi = model.jnt_range[j]
        sid, cn = JOINT_INFO.get(name, ('?', name))
        import math
        lines.append(f"{j:>2}  {name:<16} {str(sid):>3}  {cn:<14} "
                     f"{math.degrees(lo):+.1f} ~ {math.degrees(hi):+.1f}")
    lines.append('')
    lines.append('真机第 15 颗：嘴（ID 34）不在步行仿真里（走路不动嘴）。')
    return '\n'.join(lines)


def load_model():
    """用 VFS（内存虚拟文件系统）加载模型。
    原因：MuJoCo 的 C++ 层用窄字符 API 打开文件，
    路径里含中文（如工作区目录名）会解析成乱码打不开。
    把 XML 和全部网格读进内存再交给它，绕开文件路径。"""
    import mujoco
    model_dir = os.path.dirname(SCENE)
    vfs = {}
    for fn in os.listdir(model_dir):
        if fn.endswith('.xml'):
            with open(os.path.join(model_dir, fn), 'rb') as f:
                vfs[fn] = f.read()
    adir = os.path.join(model_dir, 'assets')
    for fn in os.listdir(adir):
        with open(os.path.join(adir, fn), 'rb') as f:
            vfs['assets/' + fn] = f.read()
    with open(SCENE, 'r', encoding='utf-8') as f:
        xml = f.read()
    return mujoco.MjModel.from_xml_string(xml, vfs)


def main():
    import mujoco
    model = load_model()
    data = mujoco.MjData(model)

    print('=== Microduck：仿真关节 ↔ 舵机 ID 对照 ===')
    print(joint_table(model))
    print()

    kf_names = [mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_KEY, i)
                for i in range(model.nkey)]
    print(f'姿势关键帧: ' + ', '.join(f'{i+1}={n}' for i, n in enumerate(kf_names)))

    if '--check' in sys.argv:
        # 无界面自检：逐个姿势加载，打印每个关节角度（度）
        import math
        for i, kn in enumerate(kf_names):
            mujoco.mj_resetDataKeyframe(model, data, i)
            mujoco.mj_forward(model, data)
            angles = []
            for j in range(model.njnt):
                name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, j)
                if name in JOINT_INFO:
                    qadr = model.jnt_qposadr[j]
                    angles.append(f"{name}={math.degrees(data.qpos[qadr]):+.0f}")
            print(f'[{kn}] ' + ' '.join(angles))
        print('模型自检 OK（关节数 %d，网格 %d，关键帧 %d）'
              % (model.njnt, model.nmesh, model.nkey))
        return

    # 开场先摆成 STAND，让鸭子站着迎客
    if 'STAND' in kf_names:
        mujoco.mj_resetDataKeyframe(model, data, kf_names.index('STAND'))
        mujoco.mj_forward(model, data)

    def on_key(keycode):
        # 数字键 1~4 的 ASCII 码
        if ord('1') <= keycode <= ord('4'):
            idx = keycode - ord('1')
            if idx < model.nkey:
                mujoco.mj_resetDataKeyframe(model, data, idx)
                mujoco.mj_forward(model, data)
                print(f'已切到姿势: {kf_names[idx]}')

    import mujoco.viewer
    import time
    print('查看器已打开：按 1/2/3/4 切姿势；左侧面板 Joints 拖滑块掰关节。关窗口退出。')
    # mujoco 3.13 的 launch() 不收 key_callback；launch_passive 才收，且要自己跑物理循环
    with mujoco.viewer.launch_passive(model, data, key_callback=on_key) as v:
        while v.is_running():
            step_start = time.time()
            mujoco.mj_step(model, data)
            v.sync()
            # 实时节流：等满一个物理步长，否则全速跑像快进
            elapsed = time.time() - step_start
            if elapsed < model.opt.timestep:
                time.sleep(model.opt.timestep - elapsed)


if __name__ == '__main__':
    main()
