import gradio as gr
from functools import partial
import random
import os
from db import send_message_to_mongodb
all_property = ['artifact', 'color', 'lightness', 'blury', 'overall']
property_dict = {
    'artifact': 'has less artifact or noise',
    'color': 'has more pleasant color',
    'lightness': 'is well illuminated',
    'blury': 'has sharp and clear texture',
    'overall': 'is more visually plansant'
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

method_dict = {
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
        return image1, image2, f"<h2 style='font-size: 24px;'>Which one {property_dict[property]}?</h2>",\
          image, method1, method2, property, image_input, request_state
    gr.Markdown("<h2 align='center',style='font-size: 24px;'>Low-light Image Enhancer Arena 🥊</h2>")
    gr.Markdown("<p align='center', style='font-size: 18px;'>This is a simple arena to test the performance of different low-light image enhancers.</p>")
    gr.Markdown("<p align='center', style='font-size: 18px;'>Please help us to find the better image!</p>")
    with gr.Row():
        with gr.Column():
            gr.Markdown("<p style='font-size: 16px;'>Common Failures:</p>")
            gr.Markdown("<ul style='font-size: 14px;'>"
                        f"<li><strong>Artifact/Noise:</strong> - There might be unintended alterations in the image.</li>"
                        f"<li><strong>Unpleasant Color:</strong> - The color recovered from low-light input can be unnatural.</li>"
                        f"<li><strong>Poor Illumination:</strong> - The brightness of the image is unsatisfying, it might be too dark or too bright.</li>"
                        f"<li><strong>Blury/Oversmooth:</strong> - The texture of the image is unclear, possibly due to an overshooted denoising.</li>"
                        "</ul>")
            gr.Image('./cat.png', label='Example')
        img_input = gr.Image(label="Input Image")
 

    with gr.Row():
        img1 = gr.Image(label="Image 1")
        img2 = gr.Image(label="Image 2")
    
    prop_text = gr.Markdown(f'###Which one is better in terms of x?')
    image_state, method1_state, method2_state, property_state, ip_state = gr.State(), gr.State(), gr.State(), gr.State(), gr.State()
    block_demo.load(on_load, inputs=[], outputs=[img1, img2, prop_text, 
                                                   image_state, method1_state, method2_state, property_state, img_input, ip_state])
    with gr.Row():
        l_butt = gr.Button("Left one")
        r_butt = gr.Button("Right one")
    with gr.Row():
        both_good = gr.Button("Both are good")
        both_bad = gr.Button("Both are bad")

    result = gr.Markdown("")
    # l_note, r_note = gr.Markdown(""), gr.Markdown("")
    refresh_butt = gr.Button("Next one", visible=False, interactive=False)
    # good, bad = gr.State('both_good'), gr.State('both_bad')
    def update_interface(choice, image, method1, method2, property, ip):
        # if type(choice) is not str : choice = choice.value
        print(choice, image, method1, method2, property, ip)
        send_message_to_mongodb(image, property, method1, method2, choice, ip)
        # new_image, new_method1, new_method2, new_image1, new_image2, new_property = get_random_comparison()
        return [
            # gr.Markdown("### Thanks for your submission!"),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
            gr.Button(interactive=False),
            # gr.Markdown(f'Left image: {method_dict[method1]}'),
            # gr.Markdown(f'Right image: {method_dict[method2]}'),
            gr.Button(visible=True, interactive=True),
            # gr.Image(new_image1), 
            # gr.Image(new_image2),
            # f'### Submit your choice for **{new_property}**'
        ]

    l_butt.click(fn=update_interface, inputs=[method1_state, image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad, refresh_butt])
    r_butt.click(fn=update_interface, inputs=[method2_state, image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad,  refresh_butt])
    both_good.click(fn=update_interface, inputs=[gr.State('both_good'), image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad, refresh_butt])
    both_bad.click(fn=update_interface, inputs=[gr.State('both_bad'), image_state, method1_state, method2_state, property_state, ip_state], outputs=[l_butt, r_butt, both_good, both_bad, refresh_butt])


    refresh_butt.click(None, js="window.location.reload()")

block_demo.launch()