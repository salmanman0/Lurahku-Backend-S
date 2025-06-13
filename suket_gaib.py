from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle
from datetime import datetime
from gear import Align, Table, HeaderFooter, TandaTangan

align = Align()
table = Table()
head = HeaderFooter()
ttd = TandaTangan()

def create_pdf(file_path, no_surat, tanggal, romawi, tahun, terlapor, pelapor, hubungan, rt,rw, bulan_gaib, tahun_gaib, keterangan):
    doc = BaseDocTemplate(file_path, pagesize=head.letter)
    frame = Frame(doc.leftMargin, doc.bottomMargin, width=doc.width, height=doc.height - 1.8 * cm, leftPadding=4, rightPadding=3, id='normal')
    template = PageTemplate(id='header_footer', frames=frame, onPage=head.header_footer)
    doc.addPageTemplates([template])
    elements = []

    elements.append(Paragraph("<b><u>SURAT KETERANGAN GAIB</u></b>", align.center_with_leading(12,0,1.5)))
    elements.append(Paragraph(f"Nomor: {no_surat}/SKum/LB/{romawi}/{tahun}", align.center_with_leading(12,0,2)))

    text1 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>LURAH LIMBUNGAN KECAMATAN RUMBAI TIMUR KOTA PEKANBARU</b>, dengan ini menerangkan bahwa : "
    elements.append(Paragraph(text1, align.justify_with_leading(12,.0,1.5)))

    table.table_normal_dalam(elements, terlapor, align.justify_with_leading(12, 0, 1), 0.2*cm)

    text2 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Adalah {hubungan} dari "
    elements.append(Paragraph(text2, align.justify_with_leading(12,0, 1.5)))

    table.table_normal_dalam(elements, pelapor, align.justify_with_leading(12,0,1), 0.2*cm)    
    
    text3 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Berdasarkan Surat Pernyataan dari <b>{pelapor['Nama']}</b> dan Surat Keterangan dari Ketua RT.{rt} RW.{rw}, benar {hubungan} {pelapor['Nama']} tersebut diatas sudah tidak berada lagi di Kelurahan Limbungan sejak bulan {bulan_gaib} tahun {tahun_gaib}, dan kami tidak mengetahui lagi alamatnya (Gaib)."
    elements.append(Paragraph(text3, align.justify_with_leading(12,0,1.5)))


    text4 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demikianlah surat keterangan ini diberikan kepada yang bersangkutan untuk <b>{keterangan}</b>."
    elements.append(Paragraph(text4, align.justify_with_leading(12,0.5*cm,1.5)))
    
    ttd.tanda_tangan(elements, tanggal, align.right_with_leading(12,0,1.5))

    doc.build(elements)

# data_terlapor = {
#         "Nama": "<b>Salman Ananda M. S</b>",
#         "NIK": "1471129214912",
#         "Tempat, Tanggal Lahir": "Medan, 16 April 2002",
#         "Warga Negara": "Indonesia",
#         "Agama": "Islam",
#         "Pekerjaan": "Pegawai BUMN",
#     }
# data_pelapor = {
#       "Nama" : "<b>Salman En</b>",
#       "NIK" : "14214691892379128",
#       "Tempat, Tanggal Lahir" : "T. Tinggi, 17 April 2024 T. Tinggi, 17 April 2024",
#       "Warga Negara": "Indonesia",
#       "Agama" : "Islam",
#       "Pekerjaan" : "Mengurus Rumah Tangga",
#       "Alamat" : "Jl. Jalan, Julun",
#     }
# create_pdf("static/file/suket-gaib.pdf", "2", "12 Oktober 2024", romawi, tahun, data_terlapor, data_pelapor,"Suami", "02", "10", "Oktober", "2018", "gugatan perceraian")