from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle
from datetime import datetime
from gear import Align, Table, HeaderFooter, TandaTangan

align = Align()
table = Table()
head = HeaderFooter()
ttd = TandaTangan()

romawi = ""
waktu = datetime.now()
tahun = waktu.strftime("%Y")
bulan = waktu.strftime("%m")
hari = waktu.strftime("%d")

if bulan == "1" :
  romawi = "I"
elif bulan == "2" :
  romawi = "II"
elif bulan == "3" :
  romawi = "III"
elif bulan == "4" :
  romawi = "IV"
elif bulan == "5" :
  romawi = "V"
elif bulan == "6" :
  romawi = "VI"
elif bulan == "7" :
  romawi = "VII"
elif bulan == "8" :
  romawi = "VIII"
elif bulan == "9" :
  romawi = "IX"
elif bulan == "10" :
  romawi = "X"
elif bulan == "11" :
  romawi = "XI"
elif bulan == "12" :
  romawi = "XII"
else:
  romawi = "Terjadi kesalahan"

def create_pdf(file_path, no_surat, tanggal, romawi, tahun, terlapor, hari_meninggal, pelapor):
    doc = BaseDocTemplate(file_path, pagesize=head.A4)
    frame = Frame(doc.leftMargin, doc.bottomMargin, width=doc.width, height=doc.height - 1.8 * cm, leftPadding=4, rightPadding=3, id='normal')
    template = PageTemplate(id='header_footer', frames=frame, onPage=head.header_footer)
    doc.addPageTemplates([template])
    elements = []

    elements.append(Paragraph("<b><u>SURAT KETERANGAN KEMATIAN</u></b>", align.center_with_leading(12,0,1.5)))
    elements.append(Paragraph(f"Nomor:   /SKK/LB/{romawi}/{tahun}", align.center_with_leading(12,0,2)))

    text1 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>LURAH LIMBUNGAN KECAMATAN RUMBAI TIMUR KOTA PEKANBARU</b>, dengan ini menerangkan bahwa : "
    elements.append(Paragraph(text1, align.justify_with_leading(12,.0,1.5)))

    table.table_normal(elements, terlapor, align.justify_with_leading(12, 0, 1),0.2*cm)

    text2 = "<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Orang tersebut benar telah <b>Meninggal Dunia</b> pada : "
    elements.append(Paragraph(text2, align.justify_with_leading(12,0, 1.5)))

    table.table_normal(elements, hari_meninggal, align.justify_with_leading(12,0,1), 0.2*cm)

    text3 = "<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Surat Keterangan ini dibuat berdasarkan laporan dari : "
    elements.append(Paragraph(text3, align.justify_with_leading(12,0,1.5)))

    table.table_normal(elements, pelapor, align.justify_with_leading(12,0,1), 0.2*cm)    

    text4 = "<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demikian Surat Keterangan ini kami buat, untuk dipergunakan sebagaimana mestinya. "
    elements.append(Paragraph(text4, align.justify_with_leading(12,0.5*cm,1.5)))
    
    ttd.tanda_tangan(elements, tanggal, align.right_with_leading(12,0,1.5))

    doc.build(elements)