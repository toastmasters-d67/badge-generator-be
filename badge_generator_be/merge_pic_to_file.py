from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_pdf(image_paths, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter

    # Calculate the number of pages needed
    num_pages = len(image_paths) // 4 + (1 if len(image_paths) % 4 != 0 else 0)
    print('num_pages:', num_pages)

    for i in range(num_pages):
        if i != 0:
            c.showPage()
        c.setFont("Helvetica", 12)
        for j in range(4):
            index = i * 4 + j
            if index < len(image_paths):
                x_offset = (j % 2) * (width / 2) + 20
                y_offset = (1 - (j // 2)) * (height / 2) + 20
                image_path = image_paths[index]
                try:
                    c.drawImage(image_path, x_offset, y_offset, width / 2 - 40, height / 2 - 40)
                except Exception as e:
                    print(f"Error adding image {image_path}: {e}")

    c.save()
