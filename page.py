import gradio as gr
from model import get_content, category_specific, get_overview_content
import existed_report
import json, datetime

css = """
.title_page {
    # margin-left:24vw;
    width: 58.5vw;
    height:65vh;
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
            year = gr.Dropdown(['2020', '2021', '2022', '2023'], label='year', value='2023')
            season = gr.Dropdown(['Spring/Summer (S/S)', 'Autumn/Winter (A/W)'], label='season',
                                 value='Spring/Summer (S/S)')
            category = gr.Dropdown(
                ['Dresses&Skirts', 'Jackets&Coats&Outerwear', 'Topweights', 'Trousers&Shorts'],
                value='Dresses&Skirts', label='category')
            brand = gr.CheckboxGroup(
                ['chanel', 'christian-dior', 'givenchy', 'louis-vuitton', 'saint-laurent', 'valentino'],
                value=['chanel'], label='brand')
            generative_model = gr.Dropdown(['GPT', 'gemini'], value='GPT', label='model')
            api_key = gr.Textbox(label='api key')
            new_report = gr.Checkbox(label='new report')
            check_exist = gr.Button(value='check existed report')
            # check_result = gr.Markdown()
            generate = gr.Button(value='generate')
        with gr.Column(scale=3):
            with gr.Column(elem_classes=['title_page']):
                with gr.Row():
                    with gr.Column(scale=1):
                        # gr.Markdown("# Title page")
                        content = gr.Markdown()
                    with gr.Column(scale=2):
                        cover_img = gr.Image(min_width=500)
    with gr.Row():
        with gr.Column(elem_classes=['page2']):
            with gr.Row():
                with gr.Column(variant='panel', scale=1):
                    gr.Markdown("# Overview")
                    description = gr.Markdown()
                with gr.Column(variant='panel', scale=2):
                    chart_path = gr.Image()
                    line_path = gr.Image()
                with gr.Column(variant='panel', scale=1):
                    img1 = gr.Image()
                    img2 = gr.Image()
                    img3 = gr.Image()
    # section = list()
    # sub_section0 = section[0] if len(section) > 0 else " "
    # sub_section1 = section[1] if len(section) > 1 else " "

    with gr.Column(elem_classes=['page2']):
        gr.Markdown('# ' + category_specific[category.value][0])
        section_description = gr.Markdown()
        with gr.Row():
            with gr.Column(scale=2):
                with gr.Tab("silhouette"):
                    section_fig1 = gr.Image()
                with gr.Tab("detail"):
                    section_fig2 = gr.Image()
            with gr.Column(scale=1):
                with gr.Row():
                    section_fig3 = gr.Image()
                with gr.Row():
                    section_fig4 = gr.Image()
    with gr.Column(elem_classes=['page2']):
        gr.Markdown('# ' + category_specific[category.value][1])
        section_description2 = gr.Markdown()
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Tab("silhouette"):
                    section_fig5 = gr.Image()
                with gr.Tab("detail"):
                    section_fig6 = gr.Image()
            with gr.Column(scale=1):
                with gr.Row():
                    section_fig7 = gr.Image()
                    section_fig8 = gr.Image()

    overview_dict = gr.Json(visible=False)
    section_dict = gr.Json(visible=False)

    check_exist.click(fn=existed_report.return_exist_report, inputs=[year, season, category, brand, generative_model],
                      outputs=[cover_img, content, description, chart_path, line_path, img1, img2, img3,
                               section_fig1, section_fig2,
                               section_fig3, section_fig4, section_description, section_fig5, section_fig6,
                               section_fig7,
                               section_fig8, section_description2, overview_dict, section_dict])

    generate.click(fn=get_content, inputs=[year, season, category, brand, new_report, generative_model, api_key],
                   outputs=[cover_img, content, description, chart_path, line_path, img1, img2, img3,
                            section_fig1, section_fig2,
                            section_fig3, section_fig4, section_description, section_fig5, section_fig6, section_fig7,
                            section_fig8, section_description2, overview_dict, section_dict])

demo.launch(share=False)
