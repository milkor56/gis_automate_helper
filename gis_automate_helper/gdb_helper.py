import arcpy, os


def extract_photos_from_fgdb(fgdb, fc, photo_name_fields, photo_folder, sql):
    arcpy.env.workspace = fgdb
    tables = arcpy.ListTables()
    if fc in arcpy.ListFeatureClasses():
        table = fc + "__ATTACH"
        if table in tables:
            arcpy.MakeTableView_management(os.path.join(arcpy.env.workspace, table), table)
            arcpy.AddJoin_management(table, "REL_GLOBALID", fc, "GLOBALID")
            fields = arcpy.ListFields(table, None, "String")

            namingFields = []
            for field in fields:
                temp_field = field.name
                temp_field = temp_field.upper()
                for fld in photo_name_fields:
                    if temp_field.find(fld.upper()) != -1:
                        namingFields.append(field.name)

            # print([table + '.DATA'] + namingFields)
            # print(fgdb)
            with arcpy.da.SearchCursor(table, [table + '.DATA'] + namingFields, sql) as cursor:
                for item in cursor:
                    photoname = ""
                    i = 0
                    photoname = ""
                    while i < len(namingFields):
                        if item[i + 1] is not None:
                            photoname += str(item[i + 1]) + "_"
                        i += 1
                    if photoname == "":
                        photoname = "UNKNOWN"
                    attachment = item[0]
                    filename = os.path.join(photo_folder, photoname + "0.jpg")
                    filename = filename.replace("/", '')
                    suffix = 1
                    while os.path.exists(filename):
                        filename = filename[:-5] + str(suffix) + ".jpg"
                        suffix += 1
                        # print suffix
                    open(filename, 'wb').write(attachment.tobytes())

    return True