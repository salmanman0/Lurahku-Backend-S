from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib import colors
from datetime import datetime
from gear import Align, Table, HeaderFooter, TandaTangan

align = Align()
table = Table()
head = HeaderFooter()
ttd = TandaTangan()

def create_pdf(file_path, no_surat, tanggal, romawi, tahun, jenisUsaha, data, alamat, peraturan, keterangan):
    doc = BaseDocTemplate(file_path, pagesize=head.A4)
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        width=doc.width, height=doc.height - 1.8 * cm,
        leftPadding=4, rightPadding=3,
        id='normal'
    )
    template = PageTemplate(id='header_footer', frames=frame, onPage=head.header_footer)
    doc.addPageTemplates([template])
    elements = []

    elements.append(Paragraph("<b><u>SURAT KETERANGAN DOMISILI USAHA</u></b>", align.center(12, 2)))
    elements.append(Paragraph(f"<b>No : .../SKDU/LB/{romawi}/{tahun}</b>", align.center(12, 0.5 * cm)))

    text1 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Lurah Limbungan Kecamatan Rumbai Timur Kota Pekanbaru, dengan ini menerangkan bahwa : "
    elements.append(Paragraph(text1, align.justify_with_leading(12, 0, 1.5)))

    table.table_normal_dalam(elements, data, align.left(12, 2), 0.2 * cm)

    text3 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Benar yang bersangkutan memiliki usaha <b>“{jenisUsaha}”</b> yang berdomisili di : "
    elements.append(Paragraph(text3, align.justify_with_leading(12, 0, 1.5)))

    table.table_normal_dalam(elements, alamat, align.left(12, 1), 0.2 * cm)

    text4 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Dengan persyaratan dan ketentuan-ketentuan sebagai berikut:"
    elements.append(Paragraph(text4, align.justify_with_leading(12, 0.2 * cm, 1.5)))

    # Buat ListFlowable dari peraturan
    list_items = []
    for i, value in enumerate(peraturan.values(), start=1):
        p = Paragraph(f"{value}", align.justify_with_leading(12,0,1.5))
        list_items.append(ListItem(p, leftIndent=18))

    elements.append(ListFlowable(
        list_items,
        bulletType='1',          
        bulletFormat='%s.',      
        start='1',
        leftIndent=12,
        bulletFontSize=12,
        bulletFontName='Arial',
        spaceBefore=0.2 * cm
    ))

    text5 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demikian surat keterangan ini kami berikan kepada yang bersangkutan untuk <b>{keterangan}</b>.<br/>"
    elements.append(Paragraph(text5, align.justify_with_leading(12, 0.5 * cm, 1.5)))

    ttd.tanda_tangan(elements, tanggal, align.right_with_leading(12, 0, 1.5))

    doc.build(elements)



# data_pengajuan = {
#     "Nama": "<b>YULIAN RANDA</b>",
#     "NIK": "1471122407920041",
#     "Tempat, Tanggal Lahir": "Pekanbaru, 24-07-1992",
#     "Agama": "Islam",
#     "Pekerjaan": "Buruh Harian Lepas",
#     "Alamat": "Jl. Teluk Leok RT.01 RW.01 Kel. Limbungan"
# }

# alamat_pengajuan = {
#     "Alamat": "Jl. Teluk Leok RT.01 RW.01 Kel. Limbungan",
#     "Nama": "Limbungan",
#     "NIK": "Rumbai Timur",
#     "Kota": "Pekanbaru"
# }
# peraturan = {
#     "1": "Tidak melakukan penyalahgunaan tempat usaha;",
#     "2": "Untuk Memenuhi segala peraturan, hukum dan norma yang berlaku di wilayah Kelurahan Limbungan Kecamatan Rumbai Timur Kota Pekanbaru;",
#     "3": "Untuk selalu menjaga kebersihan, keindahan, ketertiban dan keamanan diwilayah /lingkungan tempat usaha yang bersangkutan;",
#     "4": "Memenuhi segala kewajiban dan retribusi yang diatur sesuai dengan undang-undang yang berlaku."
# }
# nomor_surat = 650

# create_pdf("static/file/suket_domisili_usaha.pdf",nomor_surat, "10 Oktober 2024", "I", "2024", "UMKM", data_pengajuan, alamat_pengajuan, peraturan, "mama tu amam")