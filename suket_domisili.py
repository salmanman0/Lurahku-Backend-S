from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from gear import Align, Table, HeaderFooter, TandaTangan

align = Align()
table = Table()
head = HeaderFooter()
ttd = TandaTangan()

def create_pdf(file_path, no_surat, tanggal, rt, rw, alamat, romawi, tahun, pelapor, keterangan):
    doc = BaseDocTemplate(file_path, pagesize=head.A4)
    frame = Frame(doc.leftMargin, doc.bottomMargin, width=doc.width, height=doc.height - 1.8 * cm, leftPadding=4, rightPadding=3, id='normal')
    template = PageTemplate(id='header_footer', frames=frame, onPage=head.header_footer)
    doc.addPageTemplates([template])
    elements = []

    elements.append(Paragraph("<b><u>SURAT KETERANGAN DOMISILI</u></b>", align.center(12, 2)))
    elements.append(Paragraph(f"Nomor:   /SKDM/LB/{romawi}/{tahun}", align.center(12,0.5*cm)))

    text1 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Lurah Limbungan Kecamatan Rumbai Timur Kota Pekanbaru, dengan ini menerangkan bahwa : "
    elements.append(Paragraph(text1, align.justify_with_leading(12,0,1.5)))

    table.table_normal_dalam(elements, pelapor, align.left(12, 2), 0.2*cm)

    text3 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Berdasarkan Keterangan Perizinan RT. {rt} RW. {rw} benar nama tersebut diatas adalah warga yang berdomisili di {alamat} RT. {rt} RW. {rw} Kelurahan Limbungan Kec Rumbai Timur."
    elements.append(Paragraph(text3, align.justify_with_leading(12,2,1.5)))

    text4 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demikian Surat Keterangan ini dibuat dan <b>dipergunakan untuk {keterangan}</b>"
    elements.append(Paragraph(text4, align.justify_with_leading(12,1*cm,1.5)))
    
    ttd.tanda_tangan(elements, tanggal, align.right_with_leading(12,0,1.5))

    doc.build(elements)

# data_pengajuan = {
#         "Nama": "<b>Salman Ananda M. S</b>",
#         "NIK": "1471129214912",
#         "Tempat, Tanggal Lahir": "Medan, 16 April 2002",
#         "Jenis Kelamin": "Laki-Laki",
#         "Kewarganegaraan": "Indonesia",
#         "Agama": "Islam",
#         "Pekerjaan": "Belum Bekerja",
#         "Alamat": "Jl. Teluk Leok Gg. Jati RT.04 RW.03",
#     }

# no_surat = 650

# create_pdf("static/file/suket_domisili.pdf", no_surat, "12 Oktober 2024", "02", "10", "Jl. Jalan", romawi, tahun, data_pengajuan, "persyaratan masuk PNS")