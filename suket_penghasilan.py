from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle
from datetime import datetime
from gear import Align, Table, HeaderFooter, TandaTangan

align = Align()
table = Table()
head = HeaderFooter()
ttd = TandaTangan()

def create_pdf(file_path, no_surat, tanggal, romawi, tahun, pelapor, rt, rw, penghasilan, keterangan):
    doc = BaseDocTemplate(file_path, pagesize=head.letter)
    frame = Frame(doc.leftMargin, doc.bottomMargin, width=doc.width, height=doc.height - 1.8 * cm, leftPadding=4, rightPadding=3, id='normal')
    template = PageTemplate(id='header_footer', frames=frame, onPage=head.header_footer)
    doc.addPageTemplates([template])
    elements = []

    elements.append(Paragraph("<b><u>SURAT KETERANGAN PENGHASILAN</u></b>", align.center_with_leading(12,0,1.5)))
    elements.append(Paragraph(f"Nomor: {no_surat}/SKum/LB/{romawi}/{tahun}", align.center_with_leading(12,0,2)))

    text1 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>LURAH LIMBUNGAN KECAMATAN RUMBAI TIMUR KOTA PEKANBARU</b>, dengan ini menerangkan bahwa : "
    elements.append(Paragraph(text1, align.justify_with_leading(12,0,1.5)))

    table.table_normal_dalam(elements, pelapor, align.justify_with_leading(12,0,1.5), 0.2*cm)

    text2 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Nama tersebut diatas adalah benar berdomisili di {pelapor['Alamat']} Kelurahan Limbungan Kecamatan Rumbai Timur. Berdasarkan Surat Keterangan RT {rt} RW {rw} dan Surat Pernyataan bersangkutan, benar bahwa yang bersangkutan <b>memiliki penghasilan Rp. {penghasilan}.-/bulan.</b>"
    elements.append(Paragraph(text2, align.justify_with_leading(12,0, 2)))

    text3 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demikian surat keterangan ini dibuat dengan sebenarnya dan dipergunakan untuk <b>{keterangan}</b>."
    elements.append(Paragraph(text3, align.justify_with_leading(12,0.5*cm, 2)))

    ttd.tanda_tangan(elements, tanggal, align.right_with_leading(12,0,1.5))

    doc.build(elements)