# メモ：　なんかのキーを押したらキャリブレーションする
import mmap
import os
import struct

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from pyjoycon import GyroTrackingJoyCon, get_L_id


class JoyCon:
    def __init__(self):
        joycon_id = get_L_id()
        self.joycon: GyroTrackingJoyCon = GyroTrackingJoyCon(*joycon_id)

    @property
    def pointer(self):
        return self.joycon.pointer

    @property
    def rotation(self):
        return self.joycon.rotation

    @property
    def direction(self):
        return self.joycon.direction
    
    @property
    def direction_quarternion(self):
        return self.joycon.direction_Q



if __name__ == "__main__":
    # mmapの初期化
    file_name = "/tmp/joycon_direction.dat"
    file_size = 4 * 4  # float x 4 = 16 bytes

    # ファイルがなければ作成
    if not os.path.exists(file_name):
        with open(file_name, "wb") as f:
            f.write(b"\x00" * file_size)

    jc = JoyCon()
    jc.joycon.calibrate()

    # 表示領域の確保
    print("\n" * 3, end="")

    # リアルタイムプロット用の設定
    window_size = 100  # 表示するデータ点の数
    x_data = list(range(window_size))  # X軸（時間）
    y_data_1 = [0] * window_size  # センサー1のY軸データ
    y_data_2 = [0] * window_size  # センサー2のY軸データ
    y_data_3 = [0] * window_size  # センサー3のY軸データ
    y_data_4 = [0] * window_size  # センサー3のY軸データ

    # グラフのセットアップ
    fig, ax = plt.subplots()
    ax.set_ylim(-5, 5)  # Y軸の範囲を設定
    ax.set_xlim(0, window_size - 1)  # X軸の範囲を設定
    ax.set_xlabel("Time")
    ax.set_ylabel("Rotation [rad]")
    ax.set_title("Real-time JoyCon rotation")

    # ラインオブジェクトを作成
    (line1,) = ax.plot(x_data, y_data_1, label="X", color="r")
    (line2,) = ax.plot(x_data, y_data_2, label="Y", color="g")
    (line3,) = ax.plot(x_data, y_data_3, label="Z", color="b")
    (line4,) = ax.plot(x_data, y_data_4, label="W", color="y")

    ax.legend()

    # アニメーションの更新関数
    def update(frame):
        # 新しいセンサー値を取得
        new_value_1 = jc.direction_quarternion.x
        new_value_2 = jc.direction_quarternion.y
        new_value_3 = jc.direction_quarternion.z
        new_value_4 = jc.direction_quarternion.w
  

        # データを更新（FIFOで古いデータを削除）
        y_data_1.append(new_value_1)
        y_data_2.append(new_value_2)
        y_data_3.append(new_value_3)
        y_data_4.append(new_value_4)
        y_data_1.pop(0)
        y_data_2.pop(0)
        y_data_3.pop(0)
        y_data_4.pop(0)

        # グラフを更新
        line1.set_ydata(y_data_1)
        line2.set_ydata(y_data_2)
        line3.set_ydata(y_data_3)
        line4.set_ydata(y_data_4)
        
        
        with open(file_name, "r+b") as f:
            mm = mmap.mmap(f.fileno(), file_size)
            p_x = jc.pointer.x if jc.pointer else 0
            p_y = jc.pointer.y if jc.pointer else 0
            data = struct.pack(
                "ffff",
                jc.direction_quarternion.x,
                jc.direction_quarternion.y,
                jc.direction_quarternion.z,
                jc.direction_quarternion.w,
            )
            mm.seek(0)
            mm.write(data)

        return line1, line2, line3

    # アニメーションの設定
    ani = animation.FuncAnimation(fig, update, interval=100, blit=True)

    plt.show()
