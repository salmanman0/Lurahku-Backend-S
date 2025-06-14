from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import Paragraph, Table as PlatypusTable, TableStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from datetime import datetime

from reportlab.platypus import Image, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Arial', 'fonts/ARIAL.TTF'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'fonts/ARIALBD.TTF'))


def get_waktu():
    waktu = datetime.now()
    jam = waktu.strftime("%H")
    menit = waktu.strftime("%M")
    detik = waktu.strftime("%S")
    return jam, menit, detik

# Fungsi untuk mendapatkan hari, bulan, dan tahun
def get_tanggal():
    waktu = datetime.now()
    hari = waktu.strftime("%d")
    bulan = waktu.strftime("%m")
    tahun = waktu.strftime("%Y")
    return hari, bulan, tahun

def get_romawi(bulan):
    romawi = ""
    if bulan == "01":
        romawi = "I"
    elif bulan == "02":
        romawi = "II"
    elif bulan == "03":
        romawi = "III"
    elif bulan == "04":
        romawi = "IV"
    elif bulan == "05":
        romawi = "V"
    elif bulan == "06":
        romawi = "VI"
    elif bulan == "07":
        romawi = "VII"
    elif bulan == "08":
        romawi = "VIII"
    elif bulan == "09":
        romawi = "IX"
    elif bulan == "10":
        romawi = "X"
    elif bulan == "11":
        romawi = "XI"
    elif bulan == "12":
        romawi = "XII"
    else:
        romawi = "Terjadi kesalahan"
    return romawi

def get_kabisat(bulan):
    kabisat = ""
    if bulan == "01":
        kabisat = "Januari"
    elif bulan == "02":
        kabisat = "Februari"
    elif bulan == "03":
        kabisat = "Maret"
    elif bulan == "04":
        kabisat = "April"
    elif bulan == "05":
        kabisat = "Mei"
    elif bulan == "06":
        kabisat = "Juni"
    elif bulan == "07":
        kabisat = "Juli"
    elif bulan == "08":
        kabisat = "Agustus"
    elif bulan == "09":
        kabisat = "September"
    elif bulan == "10":
        kabisat = "Oktober"
    elif bulan == "11":
        kabisat = "November"
    elif bulan == "12":
        kabisat = "Desember"
    else:
        kabisat = "Terjadi kesalahan"
    return kabisat

class Align:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def justify(self, font, space):
        return ParagraphStyle('justify', parent=self.styles['Normal'], alignment=TA_JUSTIFY, fontName='Arial', fontSize=font, spaceAfter=space)
    
    def center(self, font, space):
        return ParagraphStyle('center', parent=self.styles['Normal'], alignment=1, fontName='Arial', fontSize=font, spaceAfter=space)
    
    def left(self, font, space):
        return ParagraphStyle('left', parent=self.styles['Normal'], alignment=TA_LEFT, fontName='Arial', fontSize=font, spaceAfter=space)

    def right(self, font, space):
        return ParagraphStyle('right', parent=self.styles['Normal'], alignment=TA_RIGHT, fontName='Arial', fontSize=font, spaceAfter=space)

    def justify_with_leading(self, font, space, lead):
        return ParagraphStyle('justify', parent=self.styles['Normal'], alignment=TA_JUSTIFY, fontName='Arial', fontSize=font, spaceAfter=space, leading=font*lead)
    
    def center_with_leading(self, font, space, lead):
        return ParagraphStyle('center', parent=self.styles['Normal'], alignment=1, fontName='Arial', fontSize=font, spaceAfter=space, leading=font*lead)
    
    def left_with_leading(self, font, space, lead):
        return ParagraphStyle('left', parent=self.styles['Normal'], alignment=TA_LEFT, fontName='Arial', fontSize=font, spaceAfter=space, leading=font*lead)

    def right_with_leading(self, font, space, lead):
        return ParagraphStyle('right', parent=self.styles['Normal'], alignment=TA_RIGHT, fontName='Arial', fontSize=font, spaceAfter=space, leading=font*lead)

class Table:
    @staticmethod
    def table_normal_dalam(elements, data, align_style, space):
        table_data = []
        
        for key, value in data.items():
            row = [Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {key}", align_style), ":", Paragraph(value, align_style)]
            table_data.append(row)

        table = PlatypusTable(table_data, colWidths=[7 * cm, 0.5 * cm, 8.5 * cm],spaceAfter=space)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'), 
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(table)

    @staticmethod
    def table_normal_dalam_numbering(elements, data, align_style, space):
        table_data = []
        
        for key, value in data.items():
            row = [Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {key}.", align_style), Paragraph(value, align_style, )]
            table_data.append(row)

        table = PlatypusTable(table_data, colWidths=[1.5 * cm, 14.5 * cm],spaceAfter=space)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'), 
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(table)

    @staticmethod
    def table_normal(elements, data, align_style, space):
        table_data = []
        for key, value in data.items():
            row = [Paragraph(f"{key}", align_style), ":", Paragraph(value, align_style)]
            table_data.append(row)
        table = PlatypusTable(table_data, colWidths=[7 * cm, 0.5 * cm, 8.5 * cm], spaceAfter=space)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'), 
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        elements.append(table)
    
    @staticmethod
    def table_tanggungan(elements, family_data, align_style,space):
        table_data = [["No", "Nama", "Tempat/Tgl Lahir", "Pekerjaan", "Status"]]
        
        for idx, (key, value) in enumerate(family_data.items(), start=1):
            row = [
                str(idx),  # Kolom No
                Paragraph(value['Nama'], align_style),  # Kolom Nama
                Paragraph(f"{value['Tempat/Tgl Lahir']}", align_style),  # Kolom Tempat/Tgl Lahir
                Paragraph(value['Pekerjaan'], align_style),  # Kolom Pekerjaan
                Paragraph(value['Status'], align_style)  # Kolom Status
            ]
            table_data.append(row)

        family_table = PlatypusTable(table_data, colWidths=[1 * cm, 4 * cm, 4 * cm, 4 * cm, 3 * cm], spaceAfter=space)
        family_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), 
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(family_table)

class HeaderFooter:
    def __init__(self):
        # self.F4 = (21 * cm, 33 * cm)
        # self.letter = (21.59 * cm, 27.94 * cm)
        self.A4 = (21 * cm, 29.7 * cm)
        # self.letter_size = letter
    
    def header_footer(self, canvas, doc):
        canvas.saveState()

        margin_left = 2 * cm
        margin_top = self.A4[1] - 2 * cm

        logo_path = "static/image/LimbunganLogo.jpg"
        canvas.drawImage(logo_path, margin_left, margin_top - 2.1 * cm, width=3.5 * cm, height=3.5 * cm)

        page_width = self.A4[0]
        center_x = (page_width+(margin_left/2)) / 2  # Posisi tengah horizontal canvas

        header_text_1 = "PEMERINTAH KOTA PEKANBARU"
        header_text_2 = "KELURAHAN LIMBUNGAN"
        header_text_3 = "KECAMATAN RUMBAI TIMUR"
        header_text_4 = "Jl. Sembilang – Pekanbaru"
        header_text_5 = "Kode Pos. 28261"

        canvas.setFont('Arial-Bold', 14)
        canvas.drawCentredString(center_x, margin_top + 0.5 * cm, header_text_1)

        canvas.setFont('Arial-Bold', 22)
        canvas.drawCentredString(center_x, margin_top - 0.3 * cm, header_text_2)

        canvas.setFont('Arial-Bold', 16)
        canvas.drawCentredString(center_x, margin_top - 1 * cm, header_text_3)

        canvas.setFont('Arial-Bold', 12)
        canvas.drawCentredString(center_x, margin_top - 1.5 * cm, header_text_4)

        canvas.setFont('Arial', 12)
        canvas.drawString(margin_left + 14.5 * cm, margin_top - 2 * cm, header_text_5)

        canvas.setStrokeColor(colors.black)
        canvas.setLineWidth(1)
        canvas.line(margin_left, margin_top - 2.2 * cm, self.A4[0] - margin_left, margin_top - 2.2 * cm)
        canvas.line(margin_left, margin_top - 2.25 * cm, self.A4[0] - margin_left, margin_top - 2.25 * cm)

        canvas.restoreState()



import socket

def get_local_ip():
    hostname = socket.gethostname()  # Mengambil nama host mesin
    ip_address = socket.gethostbyname(hostname)  # Mendapatkan IP address lokal
    return ip_address

class TandaTangan:
    def tanda_tangan(self, elements, tanggal, align_style):
        # Style untuk paragraf rata kiri
        left_style = ParagraphStyle(
            name='LeftAlign',
            parent=align_style,
            alignment=TA_LEFT,
            leftIndent=50
        )

        # Komponen teks dan gambar
        ttd_awal = Paragraph(f"Pekanbaru, {tanggal}<br/><b>LURAH LIMBUNGAN</b>", left_style)

        path_ttd_image = "/static/image/ttd.png"
        img_url = f"https://kelurahan-limbungan.pocari.id{path_ttd_image}"
        img = Image(img_url, width=200, height=100)  # Tanpa hAlign, karena sudah diatur oleh tabel
        img.spaceBefore = -20

        ttd_akhir = Paragraph(
            "<b><u>WELFINASARI HARAHAP, S.Sos, M.M.</u></b><br/>"
            "NIP. 19840611 200801 2 007",
            ParagraphStyle(
                name="TTDAkhir",
                parent=left_style,
                spaceBefore=-10  # Nilai negatif akan mengangkat teks ke atas, sehingga tertimpa gambar
            )
        )


        # Susun konten kolom kedua
        kolom_kedua = [ttd_awal, img, ttd_akhir]

        # Buat tabel 2 kolom: kolom 1 kosong, kolom 2 berisi tanda tangan
        data = [
            ["", kolom_kedua]
        ]

        table = PlatypusTable(data, colWidths=[200, 300])  # Atur lebar kolom sesuai kebutuhan
        table.setStyle(TableStyle([
            ("VALIGN", (1, 0), (1, 0), "TOP"),          # Konten kolom 2 dari atas
            ("ALIGN", (1, 0), (1, 0), "CENTER"),        # Gambar di tengah kolom
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ])) 

        # Tambahkan tabel ke elemen PDF
        elements.append(table)