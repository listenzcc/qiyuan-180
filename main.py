"""
File: main.py
Author: Chuncheng Zhang
Date: 2025-04-16
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    UI application for the data view broad.
    The table has 5 columns:
    | subject | session | run | name | full |
    subject: Sub_14_zhangyaxin_MEG_fMRI
    session: Day_01_fMRI_localizer
    run:     run_01 
    name:    scruaf20231128_P07_ZhouK_D242_ZhangYaXin-0003-...
    full:    /nfs/nica-history-216/180/Context_learning/Con...

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-04-16 ------------------------
# Requirements and constants
import pandas as pd
import nibabel as nib
from nicegui import ui
from rich import print

from get_files import table



# %% ---- 2025-04-16 ------------------------
# Function and class

group = table.groupby(['subject', 'session', 'run'])
indices = group.indices
print(indices.keys())

level1_options = list(set(e[0] for e in indices.keys()))


def update_level2():
    """Update level2 options: select session."""
    subject = select_level1.value
    df = table.query(f'subject == "{subject}"')

    select_level2.options = list(df['session'].unique())
    select_level2.update()
    select_level2.value = None
    select_level3.options = []
    select_level3.update()
    display_area.clear()
    show_selection()
    
def update_level3():
    """Update level3 options: select run."""
    selected_level2 = select_level2.value
    subject = select_level1.value
    session = select_level2.value
    df = table.query(f'subject == "{subject}"').query(f'session == "{session}"')

    if selected_level2:
        select_level3.options = list(df['run'].unique())
        select_level3.update()

    select_level3.value = None
    display_area.clear()
    show_selection()

def compute_df_time(df:pd.DataFrame, TR:float=2):
    n = len(df)
    n *= TR
    if n > 3600:
        return f'{n/3600:.2f} hours'
    elif n > 60:
        return f'{n/60:.2f} minutes'
    else:
        return f'{n:.2f} seconds'

import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

def show_2d_slices(data, img):
    """显示三个正交平面的2D切片"""
    # 获取中间切片
    slice_x = data[data.shape[0] // 2, :, :]
    slice_y = data[:, data.shape[1] // 2, :]
    slice_z = data[:, :, data.shape[2] // 2]
    
    # 创建Matplotlib图形
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(slice_x.T, cmap='gray', origin='lower')
    # axes[0].set_title('矢状面')
    axes[1].imshow(slice_y.T, cmap='gray', origin='lower')
    # axes[1].set_title('冠状面')
    axes[2].imshow(slice_z.T, cmap='gray', origin='lower')
    # axes[2].set_title('横断面')
    plt.tight_layout()
    
    # 转换为PNG显示
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close()
    buf.seek(0)
    
    # 在NiceGUI中显示
    with ui.card().classes('w-[40rem]'):
        ui.image(Image.open(buf))
        show_file_info(img)
    return

def show_file_info(img):
    """显示NIfTI文件元数据"""
    header = img.header
    info = f"""
    <div class="text-sm">
        <p><b>图像维度:</b> {img.shape}</p>
        <p><b>数据类型:</b> {header.get_data_dtype()}</p>
        <p><b>体素尺寸:</b> {header.get_zooms()}</p>
        <p><b>坐标系:</b> {nib.aff2axcodes(img.affine)}</p>
    </div>
    """
    ui.html(info).classes('p-4 bg-gray-100 rounded')
    return

import numpy as np
import plotly.graph_objects as go
def create_plotly_volume(data):
    """使用 plotly 创建 3D 体积渲染"""
    a, b, c = data.shape
    X, Y, Z = np.mgrid[range(a), range(b), range(c)]
    print(data.shape, X.shape, Y.shape, Z.shape)
    fig = go.Figure(data=go.Volume(
        x=X.flatten(), #data[:, 0, 0].flatten(),
        y=Y.flatten(), #data[0, :, 0].flatten(),
        z=Z.flatten(), #data[0, 0, :].flatten(),
        value=data.flatten(),
        opacity=0.1,
        surface_count=10,
    ))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), width=600)
    return fig

def create_3d_visualization(data):
    """创建3D体积渲染"""
    # 降采样以提高性能
    downsampled = data[::2, ::2, ::2]
    
    plotly_html = create_plotly_volume(downsampled)

    # 在NiceGUI中嵌入
    with ui.card().classes('w-[800px]'):
        # ui.html(plotly_html)
        ui.plotly(plotly_html)
    
def show_selection():
    """Selection results."""
    selected = {
        'subject': select_level1.value,
        'session': select_level2.value,
        'run': select_level3.value
    }

    lst = []
    for k, v in selected.items():
        if v:
            lst.append(f'{k}=="{v}"')

    if lst:
        data = table.copy().query(' & '.join(lst))
    else:
        data = table.copy()

    display_area.clear()

    with display_area:
        ui.label(f"Selection: {selected}").classes('text-sm text-gray-500')
        ui.label(f'Files: {len(data)} | {compute_df_time(data)}').classes('text-lg text-red-500')

        if selected['run']:
            ui.label('Run level')
            df = pd.DataFrame()
            df['path'] = data['full'].map(lambda e: e.as_posix())
            # df['stat'] = data['full'].map(lambda e: f'{e.stat()}')
            df = df.sort_values('path')
            df.index = range(len(df))
            ui.table.from_pandas(df).classes('max-h-80')

            img = nib.load(df['path'][0])
            data = img.get_fdata()
            affine = img.affine
            print(data.shape)

            with ui.row():
                create_3d_visualization(data)
                show_2d_slices(data, img)
                # show_file_info(img)

        elif selected['session']:
            ui.label('Session level')
            df = []
            runs = data['run'].unique()
            for i, run in enumerate(runs):
                df.append(dict(
                    run=run,
                    time=compute_df_time(data.query(f'run=="{run}"'))
                ))
            df = pd.DataFrame(df)
            ui.table.from_pandas(df).classes('max-h-80')

        elif selected['subject']:
            ui.label('Subject level')
            df = []
            sessions = data['session'].unique()
            for i, session in enumerate(sessions):
                df.append(dict(
                    session=session,
                    time=compute_df_time(data.query(f'session=="{session}"'))
                ))
            df = pd.DataFrame(df)
            ui.table.from_pandas(df).classes('max-h-80')

        # ui.button('Operation', on_click=lambda: ui.notify(f'Processing {selected}'))

# Create selection row.
with ui.row().classes('w-full p-4 bg-gray-100 rounded-lg items-center'):
    ui.label('Select file(s):').classes('mr-2')
    
    # Level 1 selection
    select_level1 = ui.select(
        options=level1_options,
        label='1: Subject',
        on_change=update_level2
    ).classes('min-w-32')
    
    # Level 2 selection
    select_level2 = ui.select(
        options=[],
        label='2: Session',
        on_change=update_level3
    ).classes('min-w-32')
    
    # Level 3 selection
    select_level3 = ui.select(
        options=[],
        label='3: Run',
        on_change=show_selection
    ).classes('min-w-32')

# Display area
display_area = ui.column().classes('w-full p-4 mt-4 border-2 rounded-lg min-h-64')

show_selection()
ui.run()

# %% ---- 2025-04-16 ------------------------
# Play ground

# %% ---- 2025-04-16 ------------------------
# Pending


# %% ---- 2025-04-16 ------------------------
# Pending
# %%

# %%
