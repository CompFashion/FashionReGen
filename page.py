import gradio as gr
from model import get_content, Result
import json

css = """
.title_page {
    # margin-left:24vw;
    width: 58.5vw;
    height:100vh;
}
.page2 {
    # margin-left:24vw;
    # width: 58.5vw;
    height:100vh;
    overflow: scroll;
}
.page2column {
    # position: static;
    width: 10vw;
    # height: 10vh;
    overflow: scroll;
}
.select {
    # position: -webkit-sticky; /* Safari */
    # position: fixed;
    top: 0;
    # padding: 10px;
    width: 20vw;
    z-index: 1000;
}
.related_img {
    height: 30vh;
    width: auto;
    object-fit: contain; /* Add this line */
    display: block; /* This ensures that the image doesn't have extra space below it */
    margin: auto;
}

"""

with gr.Blocks(css=css) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            year = gr.Dropdown(['2019', '2020', '2021', '2022', '2023', '2024'], label='year', value='2019')
            season = gr.Dropdown(['ss', 'winter'], label='season', value='ss')
            category = gr.Dropdown(
                ['blouses and woven tops', 'coats', 'dresses', 'jackets', 'jumpsuits', 'knits and jersey tops',
                 'shirts', 'shorts', 'skirts', 'sweaters', 'tops', 'trousers'],
                value='coats', label='category')
            brand = gr.CheckboxGroup(
                ['chanel', 'christian-dior', 'givenchy', 'louis-vuitton', 'saint-laurent', 'valentino'],
                value=['chanel'], label='brand')
            generate = gr.Button(value='generate')
        with gr.Column(scale=3):
            with gr.Column(variant='panel', elem_classes=['title_page']):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("# Title page")
                        content = gr.Markdown(value='default')
                    with gr.Column(scale=2):
                        gr.Image(value='content/img.png', min_width=500)
    with gr.Row():
        with gr.Column(variant='panel', elem_classes=['page2']):
            with gr.Row():
                with gr.Column(variant='panel'):
                    gr.Markdown("""
                    # Description
                    """)
                with gr.Column(variant='panel'):
                    gr.Markdown("# Charts")
                    chart_path = gr.Image()
                    gr.Image(value="content/img_1.png")
                    gr.Image(value="content/img_2.png")
                with gr.Column(variant='panel'):
                    img1 = gr.Image(elem_classes='related_img')
                    img2 = gr.Image(elem_classes='related_img')
                    img3 = gr.Image(elem_classes='related_img')
    generate.click(fn=get_content, inputs=[year, season, category, brand],
                   outputs=[chart_path, img1, img2, img3])

demo.launch(share=True)
