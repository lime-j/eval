import gradio as gr
from functools import partial
import random
import os
from db import send_message_to_mongodb
all_property = ['artifact', 'color', 'lightness', 'blury', 'overall']
property_dict = {
    'artifact': '有更少的伪影或噪点',
    'color': '颜色更赏心悦目',
    'lightness': '光照调节得当',
    'blury': '有清晰的纹理',
    'overall': '视觉上更好看'
}
methods = ['IMGS_Bread', 'IMGS_iat', 'retinexformer_png', 'images', 'IMGS_Kind', 
           'IMGS_ZeroDCE', 'IMGS_nerco', 'IMGS_quadprior', 'IMGS_LIME', 'IMGS_pairlie', 'IMGS_LD']
method_dict = {
    'IMGS_Bread': 'Bread',
    'IMGS_iat': 'IAT',
    'retinexformer_png': 'Retinexformer',
    'images': '原始输入',
    'IMGS_Kind': 'Kind',
    'IMGS_ZeroDCE': 'ZeroDCE',
    'IMGS_nerco': 'NeRCo',
    'IMGS_quadprior' : 'QuadPrior',
    'IMGS_LIME' : 'LIME',
    'IMGS_pairlie': 'PairLIE',
    'IMGS_LD' : 'LightenDiffusion',
    'IMGS_SCI' : 'SCI',
    'IMGS_pydiff' : 'PyDiff',
    'IMGS_LLFlow' : 'LLFlow'

}

method_file_dict = {
    'IMGS_Bread': 'png',
    'IMGS_iat': 'jpg',
    'retinexformer_png': 'png',
    'images': 'ori',
    'IMGS_Kind': 'ori',
    'IMGS_ZeroDCE': 'ori',
    'IMGS_nerco': 'png',
    'IMGS_quadprior' : 'png',
    'IMGS_LIME' : 'png',
    'IMGS_pairlie': 'png',
    'IMGS_LD' : 'jpg',
    'IMGS_SCI' : 'png',
    'IMGS_pydiff' : 'png',
    'IMGS_LLFlow' : 'png'

}
core_file = './file_list.txt'
bucket = os.getenv('bucket')
image_list = []
with open(core_file, 'r') as f:
    for line in f:
        if line.strip().endswith('.png'):
            image_list.append(line.strip())


class RandomState(gr.State):
    def __init__(self, image, method1, method2, property):
        super().__init__()
        self.image = image
        self.method1 = method1
        self.method2 = method2
        self.property = property


def compare_images(image1, image2):
    return "点击更好的图像。"
with gr.Blocks() as block_demo:
    
    def get_random_comparison():
        import time
        print(time.time())
        random.seed(time.time())
        image = random.choice(image_list)
        method1, method2 = random.sample(methods, 2)
        # method1_suffix, method2_suffix = 
        image1 = bucket + '/' + method1 + '/' + image
        image2 = bucket + '/' + method2 + '/' + image
        image_input = bucket + '/images/' + image
        property = random.choice(all_property)
        return image, method1, method2, image1, image2, property, image_input

    def refresh_comparison():
        return  get_random_comparison()
    def on_load(request: gr.Request):
        headers = request.headers
        host = request.client.host
        request_state = dict(headers)
        request_state['host'] = host
        # print(str(request))
        print(request_state)
        image, method1, method2, image1, image2, property, image_input = refresh_comparison()
        return image1, image2, f"<h2 style='font-size: 24px;'>哪一个{property_dict[property]}？</h2>",\
          image, method1, method2, property, image_input, request_state
    gr.Markdown("<h2 align='left',style='font-size: 24px;'>低光照图像增强擂台</h2>")
    gr.Markdown("<p align='left', style='font-size: 18px;'>我们希望通过我们精心准备的一系列暗光图像，测试不同低光照图像增强器的性能。</p>")
    gr.Markdown("<p align='left', style='font-size: 18px;'>请帮助我们找出更好的图像。</p>")
    with gr.Row():
        with gr.Column():
            gr.Markdown("<p style='font-size: 16px;'>常见问题：</p>")
            gr.Markdown("<ul style='font-size: 14px;'>"
                        f"<li><strong>伪影/噪点：</strong> - 经过增强器处理的图像可能出现未被抑制的噪声或新增添的伪影。</li>"
                        f"<li><strong>不自然的颜色：</strong> - 低光照图像颜色会发生偏移，增强器有时无法将图像校正成合适的颜色。</li>"
                        f"<li><strong>照明不佳：</strong> - 增强算法调整的程度不合适，导致过暗或过亮。</li>"
                        f"<li><strong>模糊/过度平滑：</strong> - 图像的纹理不清晰，可能是由于过度去噪造成的。</li>"
                        "</ul>")
            gr.Image('./cat_zh.png', label='示例')
        img_input = gr.Image(label="输入图像")
 

    with gr.Row():
        img1 = gr.Image(label="图像 1")
        img2 = gr.Image(label="图像 2")
    
    prop_text = gr.Markdown(f'###哪一个更好？')
    image_state, method1_state, method2_state, property_state, ip_state = gr.State(), gr.State(), gr.State(), gr.State(), gr.State()
    block_demo.load(on_load, inputs=[], outputs=[img1, img2, prop_text, 
                                                   image_state, method1_state, method2_state, property_state, img_input, ip_state])
    with gr.Row():
        l_butt = gr.Button("左边的")
        r_butt = gr.Button("右边的")
    with gr.Row():
        both_good = gr.Button("两者都好")
        both_bad = gr.Button("两者都不好")

    result = gr.Markdown("")
    # l_note, r_note = gr.Markdown(""), gr.Markdown("")
    refresh_butt = gr.Button("下一个", visible=False, interactive=False)
    # good, bad = gr.State('both_good'), gr.State('both_bad')
    def update_interface(choice, image, method1, method2, property, ip):
        # if type(choice) is not str : choice = choice.value
        print(choice, image, method1, method2, property, ip)
        send_message_to_mongodb(image, property, method1, method2, choice, ip)
        # new_image, new_method1, new_method2, new_image1, new_image2, new_property = get_random_comparison()
        return [
            # gr.Markdown("### 感谢您的提交！"),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
            # gr.Markdown(f'左图: {method_dict[method1]}'),
            # gr.Markdown(f'右图: {method_dict[method2]}'),
            gr.Button(visible=True, interactive=True),
            # gr.Image(new_image1), 
            # gr.Image(new_image2),
            # f'### 提交您对**{new_property}**的选择'
        ]

    l_butt.click(fn=update_interface, inputs=[method1_state, image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad, refresh_butt])
    r_butt.click(fn=update_interface, inputs=[method2_state, image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad,  refresh_butt])
    both_good.click(fn=update_interface, inputs=[gr.State('both_good'), image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad, refresh_butt])
    both_bad.click(fn=update_interface, inputs=[gr.State('both_bad'), image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad, refresh_butt])


    refresh_butt.click(None, js="window.location.reload()")

block_demo.launch()