import urllib, time, os, zipfile, urllib2, shutil, json

from arcrest import agol
from arcrest.security import AGOLTokenSecurityHandler
from arcrest.ags.layer import FeatureLayer
from gis_etl import read_excel
from gis_etl import read_csv


def pp(obj):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))


def get_replica(feature_service_url, layers, username, password, out_folder, export_with_date):
    token = get_token(username=username, password=password)

    fs = agol.services.FeatureService(feature_service_url, token)

    try:
        response = fs.createReplica(replicaName="GDB_bu", layers=layers,
                                    returnAttachments=True, returnAttachmentsDatabyURL=True, async=True,
                                    attachmentsSyncDirection='bidirectional', dataFormat="filegdb", out_path=out_folder)
    except urllib.request.HTTPError:
        raise Exception("\thttp error for " + feature_service_url)

    if not response:
        raise Exception("Could not get a response for " + feature_service_url)
    if 'error' in response:
        raise Exception(pp(response))

    complete = False
    while not complete:
        time.sleep(5)
        if fs.replicaStatus(response["statusUrl"])['status'] == 'Completed':
            complete = True

    dlUrl = fs.replicaStatus(response["statusUrl"])['resultUrl']
    dlFile = os.path.join(out_folder, os.path.split(dlUrl)[-1])

    req = urllib2.urlopen(dlUrl + '?token=' + token.token)
    with open(dlFile, 'wb') as fp:
        shutil.copyfileobj(req, fp)

    with zipfile.ZipFile(dlFile, 'r') as zip:
        zippeGdbName = os.path.split(zip.namelist()[0])[0]
        zip.extractall(out_folder)
    os.remove(dlFile)
    if export_with_date:
        localGdbName = feature_service_url.split('/')[-2] + "_" + time.strftime("%Y%m%d_%H%M", time.localtime()) + ".gdb"
    else:
        localGdbName = feature_service_url.split('/')[-2] + ".gdb"
    os.rename(os.path.join(out_folder, zippeGdbName), os.path.join(out_folder, localGdbName))

    return os.path.join(out_folder, localGdbName)


def get_token(username, password):
    try:
        token = AGOLTokenSecurityHandler(username=username, password=password)
    except Exception as err:
        raise Exception("Trouble getting a security token; are your credentials correct?")

    return token


def bulk_upload_attachments_from_table(feature_service_url, username, password, xls_field_match_fld,
                                       agol_field_match_fld, xls_file_name_fld, table_file, *worksheet_name,
                                       *attach_folder):
    token = get_token(username=username, password=password)

    fs = FeatureLayer(feature_service_url, token)
    if "xls" in table_file:
        rows = read_excel(excel_file=table_file, excel_worksheet_name=worksheet_name)
    elif "csv" in table_file:
        rows = read_csv(csv_file=table_file)

    for row in rows:
        if attach_folder:
            filename = os.path.join(attach_folder, row[xls_file_name_fld])
        else:
            filename = row[xls_field_match_fld]

        feature = fs.query(where=agol_field_match_fld + "='" + str(row[xls_field_match_fld]) + "'", returnIDsOnly=True)

        if not feature['objectIds']:
            print("not on agol " + str(row[xls_field_match_fld]))
        else:
            attached = fs.addAttachment(feature['objectIds'][0], filename)
            if attached:
                print("attached " + str(feature['objectIds'][0]))
            else:
                print("failed to attach " + str(row[xls_field_match_fld]))
