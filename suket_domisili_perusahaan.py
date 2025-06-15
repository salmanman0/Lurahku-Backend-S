from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from gear import Align, Table, HeaderFooter, TandaTangan

align = Align()
table = Table()
head = HeaderFooter()
ttd = TandaTangan()

def create_pdf(file_path, no_surat, tanggal, romawi, tahun, namaNotaris, noAkta, tanggalAkta, rt, rw, perusahaan, domisili, keterangan):
    doc = BaseDocTemplate(file_path, pagesize=head.A4)
    frame = Frame(doc.leftMargin, doc.bottomMargin, width=doc.width, height=doc.height - 1.8 * cm, leftPadding=4, rightPadding=3, id='normal')
    template = PageTemplate(id='header_footer', frames=frame, onPage=head.header_footer)
    doc.addPageTemplates([template])
    elements = []

    elements.append(Paragraph("<b><u>SURAT KETERANGAN DOMISILI PERUSAHAAN</u></b>", align.center(12, 2)))
    elements.append(Paragraph(f"<b>No : {no_surat}/SKU/LB/{romawi}/{tahun}</b>", align.center(12,0.5*cm)))

    text1 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Lurah Limbungan Kecamatan Rumbai Timur Kota Pekanbaru, dengan ini menerangkan bahwa : "
    elements.append(Paragraph(text1, align.justify_with_leading(12,0,1.5)))

    table.table_normal_dalam(elements, perusahaan, align.left(12, 2), 0.2*cm)

    text3 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Berdasarkan Salinan Notaris <b>{namaNotaris}</b> Nomor: {noAkta} tanggal {tanggalAkta} dan Keterangan Perizinan dari RT.{rt} RW.{rw}, benar <b>{perusahaan['Nama Perusahaan']}</b> tersebut diatas berdomisili di : "
    elements.append(Paragraph(text3, align.justify_with_leading(12,0,1.5)))

    table.table_normal_dalam(elements, domisili, align.left(12, 1), 0.2*cm)    

    text4 = f"&nbsp;&nbsp;&nbsp;&nbsp;Demikian Surat Keterangan ini kami berikan kepada yang bersangkutan untuk <b>{keterangan}</b> <br/>"
    elements.append(Paragraph(text4, align.justify_with_leading(12,1*cm,1.5)))
    
    ttd.tanda_tangan(elements, tanggal, align.right_with_leading(12,0,1.5))

    doc.build(elements)

# data_perusahaan = {
#     "Nama Perusahaan": "<b>CV. TOSINDO CONSULTANT</b>",
#     "Nama": "<b>AFIF WIBISONO</b>",
#     "Jabatan": "<b>Direktur Utama</b>",
#     "NIK": "<b>1407120409930004</b>",
# }

# domisili_perusahaan = {
#     "Jalan": "Jl. Cemara Regency Park No.04 RT.02 RW.10",
#     "Kelurahan": "Limbungan",
#     "Kecamatan": "Rumbai Timur",
#     "Kota": "Pekanbaru",
# }

# nomor_surat = 650

# create_pdf("static/file/suket_domisili_perusahaan.pdf",nomor_surat, "12 Oktober 2024", "X", "2004", "ILHAM JR", "12", "12 Oktober 2007", "02", "10", data_perusahaan, domisili_perusahaan, "mamam tu mamam")