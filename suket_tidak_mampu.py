from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from gear import Align, Table, HeaderFooter, TandaTangan

align = Align()
table = Table()
head = HeaderFooter()
ttd = TandaTangan()

def create_pdf(file_path,no_surat, tanggal, romawi, tahun, pelapor, alamat , rt, rw, keterangan):
    doc = BaseDocTemplate(file_path, pagesize=head.A4)
    frame = Frame(doc.leftMargin, doc.bottomMargin, width=doc.width, height=doc.height - 1.8 * cm, leftPadding=4, rightPadding=3, id='normal')
    template = PageTemplate(id='header_footer', frames=frame, onPage=head.header_footer)
    doc.addPageTemplates([template])
    elements = []

    elements.append(Paragraph("<b><u>SURAT KETERANGAN TIDAK MAMPU</u></b>", align.center(12, 2)))
    elements.append(Paragraph(f"<b>No : .../SKTM/LB/{romawi}/{tahun}</b>", align.center(12,0.5*cm)))

    text1 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Lurah Limbungan Kecamatan Rumbai Timur Kota Pekanbaru, dengan ini menerangkan bahwa : "
    elements.append(Paragraph(text1, align.justify_with_leading(12,0,1.5)))

    table.table_normal_dalam(elements, pelapor, align.left(12, 2), 0.2*cm)

    text3 = f"<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Berdasarkan Surat Keterangan RT. {rt} RW. {rw} benar nama tersebut berdomisili di {alamat} RT. {rt} RW. {rw} Kelurahan Limbungan dan termasuk Keluarga <b>Kurang Mampu</b>. <br/>"
    elements.append(Paragraph(text3, align.justify_with_leading(12,2,1.5)))

    text4 = f"<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demikian Surat Keterangan ini dibuat untuk <b>{keterangan}</b> <br/>"
    elements.append(Paragraph(text4, align.justify_with_leading(12,1*cm,1.5)))
    
    ttd.tanda_tangan(elements, tanggal, align.right_with_leading(12, 0, 1.5))

    doc.build(elements)

# data_pengajuan = {
#     "Nama": "<b>Salman Ananda M. S</b>",
#     "NIK": "1471129214912",
#     "Tempat, Tanggal Lahir": "Medan, 16 April 2002",
#     "Jenis Kelamin": "Laki-Laki",
#     "Agama": "Islam",
#     "Pekerjaan": "Belum Bekerja",
#     "Alamat": "Jl. M. Rasyid Gg. Putri Salju No. 1",
# }

# nomor_surat = 650

# create_pdf("static/file/suket-tidak-mampu.pdf",nomor_surat, "12 Oktober 2024", romawi, tahun, data_pengajuan, "02", "10", "Pengajuan Beasiswa Anak")