import pytesseract
from PIL import Image, ImageDraw
import flask
import base64
import io

app = flask.Flask(__name__)

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <body>
    <form action="/ocr" method="post" enctype="multipart/form-data">
        Select image to upload:
        <input type="file" name="image" id="image">
        <input type="submit" value="Upload Image" name="submit">
    </form>
    </body>
    </html>
    """

@app.route("/ocr", methods=["POST"])
def ocr():
    # 检查是否有文件上传
    if "image" not in flask.request.files:
        return "No file part"
    
    img_file = flask.request.files["image"]
    if img_file.filename == "":
        return "No selected file"
    
    try:
        # 使用 PIL 加载图像
        img = Image.open(img_file)
        
        # 获取 OCR 文本和位置
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        
        # 绘制识别框
        draw = ImageDraw.Draw(img)
        results = []
        for i in range(len(data["text"])):
            if int(data["conf"][i]) > 0:  # 忽略置信度低的结果
                x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                text = data["text"][i]
                results.append({"text": text, "position": (x, y, w, h)})
                draw.rectangle([x, y, x + w, y + h], outline="red", width=2)

        # 将处理后的图片转换为 base64 编码
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # 返回结果页面
        result_html = f"<h1>OCR Result:</h1>"
        for result in results:
            result_html += f"<p>Text: {result['text']}, Position: {result['position']}</p>"
        result_html += f'<img src="data:image/png;base64,{img_base64}" alt="Processed Image"/>'

        return result_html

    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
