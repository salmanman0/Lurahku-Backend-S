from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from gear import Align, Table, HeaderFooter, TandaTangan

align = Align()
table = Table()
head = HeaderFooter()
ttd = TandaTangan()

romawi = ""
kabisat = ""
waktu = datetime.now()
tahun = waktu.strftime("%Y")
bulan = waktu.strftime("%m")
hari = waktu.strftime("%d")

if bulan == "1" :
  romawi = "I"
  kabisat = "Janurai"
elif bulan == "2" :
  romawi = "II"
  kabisat = "Februari"
elif bulan == "3" :
  romawi = "III"
  kabisat = "Rabu"
elif bulan == "4" :
  romawi = "IV"
  kabisat = "April"
elif bulan == "5" :
  romawi = "V"
  kabisat = "Mei"
elif bulan == "6" :
  romawi = "VI"
  kabisat = "Juni"
elif bulan == "7" :
  romawi = "VII"
  kabisat = "Juli"
elif bulan == "8" :
  romawi = "VIII"
  kabisat = "Agustus"
elif bulan == "9" :
  romawi = "IX"
  kabisat = "September"
elif bulan == "10" :
  romawi = "X"
  kabisat = "Oktober"
elif bulan == "11" :
  romawi = "XI"
  kabisat = "November"
elif bulan == "12" :
  romawi = "XII"
  kabisat = "Desember"
else:
  romawi = "Terjadi kesalahan"
  kabisat = "Terjadi kesalahan"

def create_pdf(file_path,no_surat, tanggal, romawi, tahun, alamat, rw, rt, data, nomorSPKTP, tglSPKTP, keterangan):
    doc = BaseDocTemplate(file_path, pagesize=head.A4)
    frame = Frame(doc.leftMargin, doc.bottomMargin, width=doc.width, height=doc.height - 1.8 * cm, leftPadding=4, rightPadding=3, id='normal')
    template = PageTemplate(id='header_footer', frames=frame, onPage=head.header_footer)
    doc.addPageTemplates([template])
    elements = []

    elements.append(Paragraph("<b><u>SURAT KETERANGAN PINDAH WILAYAH</u></b>", align.center(12, 2)))
    elements.append(Paragraph(f"<b>No : .../SKUm/LB/{romawi}/{tahun}</b>", align.center(12,0.5*cm)))

    text1 = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Lurah Limbungan menerangkan bahwa : "
    elements.append(Paragraph(text1, align.justify_with_leading(12,0,1.5)))

    table.table_normal_dalam(elements, data, align.left(12, 2), 0.2*cm)

    text3 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Benar yang bersangkutan memiliki sebidang tanah di {alamat} RT. {rt} RW. {rw} Kelurahan Limbungan Kecamatan Rumbai Timur Kota Pekanbaru, dimana dahulunya termasuk wilayah administrasi Kelurahan Limbungan Kecamatan Rumbai Pesisir berdasarkan Surat Pernyataan Kepemilikan/ Penguasaan Tanah Register Lurah Limbungan Nomor : {nomorSPKTP} tanggal {tglSPKTP} dan sesuai <b>Nomor 03 dan Nomor 04 tanggal 17 Juni 2003</b> tentang pemekaran wilayah dan <b>Perda Nomor 10 tahun 2019</b> tentang Pembentukan Kecamatan. "
    elements.append(Paragraph(text3, align.justify_with_leading(12,0,1.5)))

    # table.table_dalam(elements, domisili, align.left(12, 1))    

    text4 = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Demikian surat keterangan Pindah Wilayah ini kami buat untuk {keterangan}. "
    elements.append(Paragraph(text4, align.justify_with_leading(12,1*cm,1.5)))
    
    ttd.tanda_tangan(elements, tanggal, align.right_with_leading(12,0,1.5))

    doc.build(elements)

# data_pengajuan = {
#     "Nama": "<b>SAREAH</b>",
#     "Jenis Kelamin": "Perempuan",
#     "NIK": "1471124411540001",
#     "Tempat, Tanggal Lahir": "Tenayan Jaya, 04-11-1954",
#     "Agama": "Islam",
#     "Pekerjaan": "Buruh Harian Lepas",
#     "Alamat": "Jl. Teluk Leok RT.01 RW.01 Kel. Limbungan",
# }

# nomor_surat = 650

# create_pdf("static/file/suket_pindah_wilayah.pdf",nomor_surat, "12 Oktober 2024", romawi, tahun, alamat, rw, rt, data_pengajuan, keterangan)