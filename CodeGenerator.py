import qrcode

class QRCodeGenerator:
    def __init__(self):
        self.url = None

    def generate_qr_code(self, url, file, fill_color, back_color):
        self.url = url
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.url)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img.save(file)