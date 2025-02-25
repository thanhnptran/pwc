# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 15:36:18 2023
Updated on Tue Feb 25 21:10:10 2025

@author: tthanh007
"""

### Make sure you have switched to "HAN" gateway before running! ###
# https://learn.microsoft.com/en-us/rest/api/aiservices/document-models/analyze-document-from-stream?view=rest-aiservices-v4.0%20(2024-11-30)&tabs=HTTP

import pandas as pd
import requests, os, time, mimetypes, sys

endpoint = "https://xxx.cognitiveservices.azure.com" # find this in your Document Intelligence resource overview
key = "xxx" # find this in your Document Intelligence resource overview
api_version = "2024-11-30"
modelId = "prebuilt-layout"

time_format = "%Y-%m-%dT%H:%M:%S.%f"

def send_api_request(file_path):
    root_folder, filename = os.path.split(file_path)
    mime_type, encoding = mimetypes.guess_type(filename)
    file = open(file_path,'rb').read()
    
    post_headers = {
        'Content-Type': mime_type,
        'Ocp-Apim-Subscription-Key': key,
    }
    post_url = f"{endpoint}/documentintelligence/documentModels/{modelId}:analyze?api-version={api_version}"
    post_response = requests.post(post_url, headers=post_headers, data=file)
    # post_response = requests.post(post_url, headers=post_headers, data=file, verify=False)
    return post_response

def get_api_response(api_request_id):
    get_headers = {
        'Ocp-Apim-Subscription-Key': key,
    }
    get_url = f"{endpoint}/documentintelligence/documentModels/{modelId}/analyzeResults/{api_request_id}?api-version={api_version}"
    
    retry = True
    while retry:
        time.sleep(5)
        print('Waited for 5 seconds')
        get_response = requests.get(get_url,headers=get_headers)
        # get_response = requests.get(get_url,headers=get_headers, verify=False)
        get_result = get_response.json()
        if 'analyzeResult' in get_result:
            retry = False
    return get_result
        
def pdf_to_excel(input_type, path, export_mode):
    
    if input_type == 'folder':
        files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames if not f.startswith('~$') and f.endswith('.pdf')]
    elif input_type == 'file':
        if path[-3:] != 'pdf':
            print('Please ensure valid pdf file path (.pdf) for parameter path.')
            return
        files = [path]
    else: 
        print("The parameter input_type can only take either 'file' or 'folder' as value.")
        return
    
    if export_mode not in ['new','append', 'all']:
        print("The parameter export_mode can only take either 'new' (1 table per sheet) or 'append' (all tables in the same sheet, each pdf in each excel file) or 'all' (all tables of all pdf files in the same sheet) as value.")
        return
    
    if export_mode == 'all':
        writer = pd.ExcelWriter(fr"{path}\result_all_tables.xlsx")
        print('Writing to file...')
        
    number_of_pages = 0
    for file in files:
        root_folder, filename = os.path.split(file)
        print(f'Processing file "{filename}"')
        
        post_response = send_api_request(file)
        api_request_id = post_response.headers['apim-request-id']
        get_response = get_api_response(api_request_id)
        
        number_of_pages += len(get_response['analyzeResult']['pages'])
        tables = get_response['analyzeResult']['tables']
        destination_file = os.path.splitext(filename)[0] + '.xlsx'
        
        if export_mode != 'all':
            writer = pd.ExcelWriter(fr"{root_folder}\{destination_file}")
            print('Writing to file...')
        
        i=1
        for table in tables:
            df = pd.DataFrame()
            for cell in table['cells']:
                df.loc[cell['rowIndex'],0]=filename
                df.loc[cell['rowIndex'],1]=str(cell['boundingRegions'][0]['pageNumber'])
                df.loc[cell['rowIndex'],cell['columnIndex']+2] = cell['content']
            
            df.loc[0,0]='filename'
            df.loc[0,1]='pagenum'
            df.columns = df.iloc[0]
            df = df[1:]
            page_num = cell['boundingRegions'][0]['pageNumber']
            
            if export_mode == 'new':
                sheetname = f"P{page_num}-T{i}"
                df.to_excel(writer, sheet_name=sheetname, index=False)
            elif export_mode in ['append','all']:
                sheetname = "data"
                if sheetname not in writer.book.sheetnames:
                    df.to_excel(writer, sheet_name=sheetname, index=False)
                else:
                    start_row = writer.sheets[sheetname].max_row
                    df.to_excel(writer, startrow = start_row, sheet_name=sheetname, index=False)       
            
            i+=1
         
        if export_mode != 'all':
            writer.close()
            print('')
            print("Done! Output excel files are saved in the input folder.")
            print(f'Number of files processed: {len(files)}')
            print(f'Number of pages processed: {number_of_pages}')
            print('##############')
    
    if export_mode == 'all':
        writer.close()
        print('')
        print("Done! Output excel files are saved in the input folder.")
        print(f'Number of files processed: {len(files)}')
        print(f'Number of pages processed: {number_of_pages}')
        print('##############')

if __name__ == "__main__":
    args = sys.argv
    globals()[args[1]](*args[2:])
