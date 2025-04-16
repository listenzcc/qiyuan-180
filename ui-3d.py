from nicegui import ui
import nibabel as nib
import numpy as np
from scipy import ndimage
import ipyvolume as ipv
from IPython.display import display
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile
from PIL import Image

# 创建文件上传区域
upload = ui.upload(label="上传NIfTI文件 (.nii/.nii.gz)", 
                  on_upload=lambda e: process_nii_file(e)).classes('w-full')

# 创建3D可视化容器
plot_container = ui.column()

def process_nii_file(upload_event):
    """处理上传的NIfTI文件"""
    try:
        # # 读取上传的文件
        # nii_file = upload_event.content.read()

        # 将上传的文件保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.nii') as tmp_file:
            tmp_file.write(upload_event.content.read())
            tmp_path = tmp_file.name

        # 使用nibabel加载NIfTI
        img = nib.load(tmp_path)
        data = img.get_fdata()
        affine = img.affine
        
        # 清除旧内容
        plot_container.clear()
        
        with plot_container:
            ui.notify("正在处理3D可视化...")
            
            # 创建3D可视化
            fig = create_3d_visualization(data)
            
            # 显示2D切片
            show_2d_slices(data)
            
            # 显示文件信息
            show_file_info(img)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        ui.notify(f"处理文件时出错: {str(e)}", type='negative')

import plotly.graph_objects as go
from plotly.offline import plot

def create_plotly_volume(data):
    """使用 plotly 创建 3D 体积渲染"""
    data= data[::2, ::2, ::2]
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
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig
    # return plot(fig, output_type="div", include_plotlyjs="cdn")

def create_3d_visualization(data):
    """创建3D体积渲染"""
    # 降采样以提高性能
    downsampled = data[::2, ::2, ::2]
    
    # 创建ipyvolume图形
    fig = ipv.figure(width=600, height=500)
    ipv.volshow(downsampled, level=[0.2, 0.3], opacity=0.03, level_width=0.1)
    ipv.style.use('minimal')
    ipv.show()
    
    plotly_html = create_plotly_volume(data)

    # 在NiceGUI中嵌入
    with ui.card().classes('w-full'):
        # ui.html(plotly_html)
        ui.plotly(plotly_html)
    
    return fig

def show_2d_slices(data):
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
    with ui.card().classes('w-full'):
        ui.image(Image.open(buf))

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

ui.run()