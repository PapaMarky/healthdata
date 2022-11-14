from typing import Union
from datetime import datetime, timedelta

import fpdf
import argparse

from fpdf import FPDF

from applehealthtool import healthdatabase
from applehealthtool.healthdatabase import AppleHealthDatabase
from datetime import date

class BP_PDF(fpdf.FPDF):
    def __init__(self):
        super().__init__()


def parse_command_line():
    parser = argparse.ArgumentParser('Pdf Test', description='Learn how to make PDF from python')
    parser.add_argument('--db', help='Path to database where blood pressure data is stored')
    return parser.parse_args()

def get_date_months_prior(date_in: date, months: int):
    year = date_in.year
    month = date_in.month - months
    day = date_in.day
    prior_date = datetime(year, month, day)
    print(f'DATE: {prior_date}')
    return prior_date

def build_pdf(bp_data):
    pdf = FPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    # write title
    w = pdf.w - pdf.r_margin - pdf.l_margin
    h = 10
    s = 'Blood Pressure Report'
    sw = pdf.get_string_width(s)
    pdf.cell(w, h, s, ln=1, align='C')
    pdf.set_font("helvetica", '', 10)
    pdf.cell(w, h-5, f'Generated {date.today()}', ln=1, align='C')
    pdf.ln(h=pdf.lasth * 3)

    label_w = pdf.get_string_width('Start:') + 3
    pdf.cell(label_w , h-5, f'Start:', ln=0, align='R')
    pdf.cell(w, h-5, str(start_date)[:10], ln=1)
    pdf.cell(label_w , h-5, f'End:', ln=0, align='R')
    pdf.cell(w, h-5, str(end_date)[:10], ln=1)
    pdf.ln()

    date_width = None
    print(f'date_width: {date_width}')
    first_date = bp_data[0]['startDate']
    date_width = pdf.get_string_width(str(first_date)) + 3
    row_h = 6
    pdf.set_font("helvetica", '', 10)
    mw = pdf.get_string_width('M')
    data_w = mw * 3
    pdf.set_fill_color(225)
    pdf.set_font("helvetica", 'B', 10)
    border_w = 0
    row_width = date_width + 2 * data_w
    page_w = pdf.w
    page_center = page_w/2
    row_x = page_w/2 - row_width / 2

    add_table(pdf,
              bp_data,
              table_align='L',
              col_align=['C', 'R', 'R'],
              headers=['Time / Date', 'sys', 'dia'],
              highlight_color=235)

    pdf.output('BP_Report.pdf', 'F')


def add_table(pdf,
              data: list,
              table_align='L',
              headers: Union[None, list] = None,
              col_align=None,
              border_w=1,
              fg_color=0,
              bg_color=255,
              highlight_color=None):
    column_widths = []
    for row in data:
        c = 0
        for col in row:
            new_w = pdf.get_string_width(str(row[col]))
            if c >= len(column_widths):
                column_widths.append(new_w)
            else:
                column_widths[c] = max(new_w, column_widths[c])
            c += 1
    # pad widths
    pad = 4
    column_widths = [x + pad for x in column_widths]
    print(f'colw: {column_widths}')
    row_h = pdf.font_size + pad
    row_w = sum(column_widths)
    table_x = pdf.l_margin
    if isinstance(table_align, int):
        table_x = pdf.l_margin + table_align
    elif table_align == 'R':
        table_x = pdf.w - pdf.r_margin - row_w
    elif table_align == 'C':
        table_x = pdf.w / 2 - row_w / 2
    old_font_style = pdf.font_style
    font_family = pdf.font_family
    font_size = pdf.font_size_pt

    if headers:
        pdf.set_font(font_family, 'B', font_size)
        pdf.set_fill_color(fg_color)
        pdf.set_text_color(bg_color)

        c = 0
        pdf.set_x(table_x)
        for header in headers:
            pdf.cell(column_widths[c], row_h,  header, ln=0, border=border_w, align='C', fill=True)
            c += 1
        pdf.ln()

    pdf.set_font(font_family, '', font_size)
    pdf.set_text_color(fg_color)
    odd_row = True
    for row in data:
        c = 0
        pdf.set_x(table_x)
        row_bg_color = highlight_color if highlight_color is not None and odd_row else bg_color
        pdf.set_fill_color(row_bg_color)
        odd_row = not odd_row

        for cname in row:
            align = ''
            if col_align:
                align = col_align[c]
            pdf.cell(column_widths[c], row_h, str(row[cname]), ln=0, border=border_w, fill=highlight_color is not None, align=align)

            c += 1
        pdf.ln()

    pdf.font_style = old_font_style

if __name__ == '__main__':
    arg_list = parse_command_line()
    print(f'ARGS: {arg_list}')

    db = AppleHealthDatabase()
    db.open_database(arg_list.db)
    end_date = date.today()
    start_date = get_date_months_prior(end_date, 3)
    source = 'Health'
    # source = 'FitCloudPro'
    bp_data = db.get_blood_pressure_report(start_date, end_date, source)
    print(f'ROWS: {len(bp_data)}')
    if len(bp_data) > 0:
        build_pdf(bp_data)
