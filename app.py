import gradio as gr
from functools import partial
import random
import os
from db import send_message_to_mongodb
import locale

all_property = ['artifact', 'color', 'lightness', 'blury', 'overall']
property_dict = {
    'artifact': 'has less artifact or noise',
    'color': 'has more pleasant color',
    'lightness': 'is well illuminated',
    'blury': 'has sharp and clear texture',
    'overall': 'is more visually plansant'
}
property_dict_zh = {
    'artifact': '有更少的伪影或噪点',
    'color': '有更悦目的颜色',
    'lightness': '照明效果更好',
    'blury': '有更清晰的纹理',
    'overall': '视觉效果更佳'
}
methods = ['IMGS_Bread', 'IMGS_iat', 'retinexformer_png', 'images', 'IMGS_Kind', 
           'IMGS_ZeroDCE', 'IMGS_nerco', 'IMGS_quadprior', 'IMGS_LIME', 'IMGS_pairlie', 'IMGS_LD']
method_dict = {
    'IMGS_Bread': 'Bread',
    'IMGS_iat': 'IAT',
    'retinexformer_png': 'Retinexformer',
    'images': 'Original Input',
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

method_text_dict = {
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
    return "Click on the better image."

def is_chinese_browser(request):
    accept_language = request.headers.get('Accept-Language', '')
    return ('zh' in accept_language.lower()) or ('zh-cn' in accept_language.lower())

with gr.Blocks() as block_demo:
    
    def get_random_comparison():
        import time
        print(time.time())
        random.seed(time.time())
        image = random.choice(image_list)
        method1, method2 = random.sample(methods, 2)
        image1 = bucket + '/' + method1 + '/' + image
        image2 = bucket + '/' + method2 + '/' + image
        image_input = bucket + '/images/' + image
        property = random.choice(all_property)
        return image, method1, method2, image1, image2, property, image_input

    def refresh_comparison():
        return get_random_comparison()

    def on_load(request: gr.Request):
        headers = request.headers
        host = request.client.host
        request_state = dict(headers)
        request_state['host'] = host
        print(request_state)
        image, method1, method2, image1, image2, property, image_input = refresh_comparison()
        is_chinese = is_chinese_browser(request)
        property_text = property_dict_zh[property] if is_chinese else property_dict[property]
        title = "哪一个" if is_chinese else "Which one"
        return image1, image2, f"<h2 style='font-size: 24px;'>{title}{property_text}?</h2>",\
          image, method1, method2, property, image_input, request_state, is_chinese

    def get_localized_text(text_en, text_zh, is_chinese):
        return text_zh if is_chinese else text_en

    img1, img2, prop_text, image_state, method1_state, method2_state, property_state, img_input, ip_state, is_chinese_state = gr.State(), gr.State(), gr.State(), gr.State(), gr.State(), gr.State(), gr.State(), gr.State(), gr.State(), gr.State(False)
    # is_chinese_state = gr.State(False)
    block_demo.load(on_load, inputs=[], outputs=[
        img1, img2, prop_text, image_state, method1_state, method2_state, property_state, img_input, ip_state, is_chinese_state
    ])

    def render_interface(is_chinese):
        title = "低光照图像增强竞技场 🥊" if is_chinese else "Low-light Image Enhancer Arena 🥊"
        subtitle1 = "这是一个简单的竞技场，用于测试不同低光照图像增强器的性能。" if is_chinese else "This is a simple arena to test the performance of different low-light image enhancers."
        subtitle2 = "请帮助我们找出更好的图像！" if is_chinese else "Please help us to find the better image!"
        common_failures = "常见问题：" if is_chinese else "Common Failures:"
        artifact_noise = "伪影/噪点：图像中可能存在意外的改变。" if is_chinese else "Artifact/Noise: There might be unintended alterations in the image."
        unpleasant_color = "不自然的颜色：从低光照输入恢复的颜色可能不自然。" if is_chinese else "Unpleasant Color: The color recovered from low-light input can be unnatural."
        poor_illumination = "照明不佳：图像的亮度不令人满意，可能太暗或太亮。" if is_chinese else "Poor Illumination: The brightness of the image is unsatisfying, it might be too dark or too bright."
        blurry_oversmooth = "模糊/过度平滑：图像的纹理不清晰，可能是由于过度去噪。" if is_chinese else "Blury/Oversmooth: The texture of the image is unclear, possibly due to an overshooted denoising."
        example_label = "示例" if is_chinese else "Example"
        input_image_label = "输入图像" if is_chinese else "Input Image"
        image1_label = "图像 1" if is_chinese else "Image 1"
        image2_label = "图像 2" if is_chinese else "Image 2"
        left_button = "左边的" if is_chinese else "Left one"
        right_button = "右边的" if is_chinese else "Right one"
        both_good_button = "两者都好" if is_chinese else "Both are good"
        both_bad_button = "两者都不好" if is_chinese else "Both are bad"
        next_button = "下一个" if is_chinese else "Next one"

        gr.Markdown(f"<h2 align='center',style='font-size: 24px;'>{title}</h2>")
        gr.Markdown(f"<p align='center', style='font-size: 18px;'>{subtitle1}</p>")
        gr.Markdown(f"<p align='center', style='font-size: 18px;'>{subtitle2}</p>")
        with gr.Row():
            with gr.Column():
                gr.Markdown(f"<p style='font-size: 16px;'>{common_failures}</p>")
                gr.Markdown("<ul style='font-size: 14px;'>"
                            f"<li><strong>{artifact_noise}</strong></li>"
                            f"<li><strong>{unpleasant_color}</strong></li>"
                            f"<li><strong>{poor_illumination}</strong></li>"
                            f"<li><strong>{blurry_oversmooth}</strong></li>"
                            "</ul>")
                gr.Image('./cat.png', label=example_label)
            gr.Image(label=input_image_label)

        with gr.Row():
            gr.Image(label=image1_label)
            gr.Image(label=image2_label)
        
        gr.Markdown(f'### {get_localized_text("Which one is better in terms of x?", "哪一个在x方面更好？", is_chinese)}')
        with gr.Row():
            gr.Button(left_button)
            gr.Button(right_button)
        with gr.Row():
            gr.Button(both_good_button)
            gr.Button(both_bad_button)

        gr.Markdown("")
        gr.Button(next_button, visible=False, interactive=False)

    render_interface(is_chinese_state)

    def update_interface(choice, image, method1, method2, property, ip):
        print(choice, image, method1, method2, property, ip)
        send_message_to_mongodb(image, property, method1, method2, choice, ip)
        return [
            gr.Button(interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
            gr.Button(visible=True, interactive=True),
        ]

    l_butt = gr.Button()
    r_butt = gr.Button()
    both_good = gr.Button()
    both_bad = gr.Button()
    refresh_butt = gr.Button()
    # image_state, method1_state, method2_state, property_state, ip_state = gr.State(), gr.State(), gr.State(), gr.State(), gr.State()

    l_butt.click(fn=update_interface, inputs=[method1_state, image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad, refresh_butt])
    r_butt.click(fn=update_interface, inputs=[method2_state, image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad,  refresh_butt])
    both_good.click(fn=update_interface, inputs=[gr.State('both_good'), image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad, refresh_butt])
    both_bad.click(fn=update_interface, inputs=[gr.State('both_bad'), image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad, refresh_butt])

    refresh_butt.click(None, js="window.location.reload()")

block_demo.launch()