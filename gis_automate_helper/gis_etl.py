import openpyxl, os, arcpy, codecs


def create_excel(outfolder, workbookname):
    if ".xlsx" not in workbookname:
        workbookname += ".xlsx"

    fname = os.path.join(outfolder, workbookname)

    if os.path.exists(fname):
        os.remove(fname)

    wb = openpyxl.Workbook()
    wb.save(os.path.join(outfolder, workbookname))

    return wb


def create_csv(outfolder, csvname):
    if ".csv" not in csvname:
        csvname += ".csv"

    fname = os.path.join(outfolder, csvname)

    if os.path.exists(fname):
        os.remove(fname)

    csvfile = codecs.open(fname, 'w', 'utf-8')

    return csvfile


def export_feature_class_to_excel(outfolder, workbookname, header_fields, fc, sql):
    wb = create_excel(outfolder=outfolder, workbookname=workbookname)
    ws = wb.active

    colcnt = 1
    for fld in header_fields:
        ws.cell(row=1, column=colcnt).value = fld
        colcnt += 1

    rowcount = 2
    for row in arcpy.da.SearchCursor(fc, header_fields, sql):
        colcnt = 1
        for fld in row:
            if fld is not None:
                ws.cell(row=rowcount, column=colcnt).value = fld
            colcnt += 1
        rowcount += 1

    wb.save(os.path.join(outfolder, workbookname))

    del ws
    del wb


def export_array_to_excel(outfolder, workbookname, header_fields, out_array):
    wb = create_excel(outfolder=outfolder, workbookname=workbookname)
    ws = wb.active

    colcnt = 1
    for fld in header_fields:
        ws.cell(row=1, column=colcnt).value = fld
        colcnt += 1

    rowcount = 2
    for row in out_array:
        colcnt = 1
        for fld in row:
            if fld is not None:
                ws.cell(row=rowcount, column=colcnt).value = fld
            colcnt += 1
        rowcount += 1

    wb.save(os.path.join(outfolder, workbookname))

    del ws
    del wb


def export_array_to_csv(outfolder, csvname, header, out_array):
    csvfile = create_csv(outfolder=outfolder, csvname=csvname)

    outstring = ""
    for field in header:
        outstring += "\"" + field + "\","

    csvfile.write(outstring[:-1])
    csvfile.write("\"\n")

    for row in out_array:
        outstring = ""
        for field in row:
            outstring += "\"" + field + "\","
        csvfile.write(outstring[:-1])
        csvfile.write("\"\n")

    csvfile.close()

    del csvfile
