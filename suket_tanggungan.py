from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, Paragraph, PageTemplate, Frame, Table
from datetime import datetime
from gear import Align, Table, HeaderFooter, TandaTangan

align = Align()
table = Table()
head = HeaderFooter()
ttd = TandaTangan()

def create_pdf(file_path, no_surat, romawi, tahun, tanggal, tgl_pengajuan, pelapor, tanggungan_data, keterangan):
    doc = BaseDocTemplate(file_path, pagesize=head.A4)
    frame = Frame(doc.leftMargin, doc.bottomMargin, width=doc.width, height=doc.height - 1.8 * cm, leftPadding=4, rightPadding=3, id='normal')
    template = PageTemplate(id='header_footer', frames=frame, onPage=head.header_footer)
    doc.addPageTemplates([template])
    elements = []

    elements.append(Paragraph("<b><u>SURAT KETERANGAN TANGGUNGAN KELUARGA</u></b>", align.center_with_leading(12, 2, 1.5)))
    elements.append(Paragraph(f"Nomor: .../SKUm/LB/{romawi}/{tahun}", align.center_with_leading(12, 0.5 * cm, 1.5))) 

    text1 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Berdasarkan Surat Pernyataan dari saudara {pelapor['Nama']} tanggal {tgl_pengajuan}, Lurah Limbungan Kecamatan Rumbai Timur Kota Pekanbaru, dengan ini menerangkan bahwa :"
    elements.append(Paragraph(text1, align.justify_with_leading(12, 0, 1.5 )))

    table.table_normal_dalam(elements, pelapor, align.left(12, 0), 0.2*cm)

    text3 = f"&nbsp;&nbsp;&nbsp;Berdasarkan pengajuan surat keterangan tanggungan keluarga pada tanggal {tgl_pengajuan} mempunyai tanggungan Keluarga sebagai berikut:"
    elements.append(Paragraph(text3, align.justify_with_leading(12, 0.5*cm, 1.5)))
    
    table.table_tanggungan(elements, tanggungan_data, align.left_with_leading(12, 0, 1.5), 0.2*cm)

    text4 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demikian Surat Keterangan ini kami buat, untuk dipergunakan {keterangan}"
    elements.append(Paragraph(text4, align.justify_with_leading(12, 0.5*cm, 1.5)))

    ttd.tanda_tangan(elements, tanggal, align.right_with_leading(12, 0, 1.5))

    doc.build(elements)