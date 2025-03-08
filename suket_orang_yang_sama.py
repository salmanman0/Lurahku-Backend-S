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

def create_pdf(file_path, no_surat, tanggal, romawi, tahun, pelapor, dataBenar, dataSalah, dokumenBenar, dokumenSalah, nomorDokumenBenar, nomorDokumenSalah, keterangan):
    doc = BaseDocTemplate(file_path, pagesize=head.F4)
    frame = Frame(doc.leftMargin, doc.bottomMargin, width=doc.width, height=doc.height - 1.8 * cm, leftPadding=4, rightPadding=3, id='normal')
    template = PageTemplate(id='header_footer', frames=frame, onPage=head.header_footer)
    doc.addPageTemplates([template])
    elements = []

    elements.append(Paragraph("<b><u>SURAT KETERANGAN ORANG YANG SAMA</u></b>", align.center_with_leading(12,0,1.5)))
    elements.append(Paragraph(f"Nomor: {no_surat}/SKum/LB/{romawi}/{tahun}", align.center_with_leading(12,0,2)))

    text1 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>LURAH LIMBUNGAN KECAMATAN RUMBAI TIMUR KOTA PEKANBARU</b>, dengan ini menerangkan bahwa : "
    elements.append(Paragraph(text1, align.justify_with_leading(12,.0,1.5)))

    table.table_normal_dalam(elements, pelapor, align.justify_with_leading(12, 0, 1), 0.2*cm)

    text2 = f"<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Berdasarkan surat pernyataan dari yang bersangkutan, benar nama {dataBenar} yang tertera pada {dokumenBenar} dengan No. {nomorDokumenBenar} dan pada {dokumenSalah} dengan No. {nomorDokumenSalah} dengan nama {dataSalah} adalah orang yang sama. Adapun Data yang benar adalah <b>{dataBenar}</b> pada {dokumenBenar}."
    elements.append(Paragraph(text2, align.justify_with_leading(12,0,1.5)))

    text4 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demikianlah surat keterangan ini diberikan kepada yang bersangkutan untuk <b>{keterangan}</b>."
    elements.append(Paragraph(text4, align.justify_with_leading(12,0.5*cm,1.5)))
    
    ttd.tanda_tangan(elements, tanggal, align.right_with_leading(12,0,1.5))

    doc.build(elements)

# data_pelapor = {
#       "Nama" : "<b>Salman En</b>",
#       "Jenis Kelamin" : "Laki-Laki",
#     }
# create_pdf("static/file/suket_orang_yang_sama.pdf", "2", "12 Oktober 2024", romawi, tahun, data_pelapor,"123412412412", "123412312", "Ijazah SMA", "2311", "10 Oktober 2018", "Salma En","gugatan perceraian")