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
    # object-fit: contain; /* Add this line */
    # display: block; /* This ensures that the image doesn't have extra space below it */
    # margin: auto;
}

"""

with gr.Blocks(css=css) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            year = gr.Dropdown(['2019', '2020', '2021', '2022', '2023'], label='year', value='2019')
            season = gr.Dropdown(['springsummer', 'winter'], label='season', value='springsummer')
            category = gr.Dropdown(
                ['Dress&Skirts', 'Jackets&Coats&Outenvear', 'Topweights', 'Trousers&Shorts'],
                value='Dress&Skirts', label='category')
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
        with gr.Column(elem_classes=['page2']):
            with gr.Row():
                with gr.Column(variant='panel', scale=2):
                    gr.Markdown("""
                    # Description
                    """)
                with gr.Column(variant='panel', scale=2):
                    gr.Markdown("# Charts")
                    chart_path = gr.Image()
                    if year != '2019':
                        bar_path = gr.Image()
                    line_path = gr.Image()
                with gr.Column(variant='panel', scale=1):
                    img1 = gr.Image()
                    img2 = gr.Image()
                    img3 = gr.Image()
    generate.click(fn=get_content, inputs=[year, season, category, brand],
                   outputs=[chart_path, bar_path, line_path, img1, img2, img3])

demo.launch(share=False)
