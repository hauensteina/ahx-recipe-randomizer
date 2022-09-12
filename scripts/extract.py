#!/usr/bin/env python

'''
Extract recipes from How to Cook Everything Fast.
Each recipe goes into a separate pdf file.
Generate a json file with recipe labels.
AHN, Sep 2022
'''

from pdb import set_trace as BP
import sys,os,random,json
import argparse
import uuid
import pdfplumber
import pikepdf
import boto3

MASTER_PDF='../bittman_fast/static/how_to_cook_everything_fast.pdf'
AWS_KEY = os.environ['AWS_KEY']
AWS_SECRET = os.environ['AWS_SECRET']

S3 = boto3.client('s3',
                  aws_access_key_id=AWS_KEY,
                  aws_secret_access_key=AWS_SECRET)
S3_BUCKET = 'ahn-uploads'
S3_FOLDER = 'bittman-fast'

def usage(printmsg=False):
    name = os.path.basename( __file__)
    msg = f'''

    Name:
      {name}: Extract recipes from How to Cook Everything Fast.
    Description:
      Each recipe goes into a separate pdf file s3://ahn-uploads/bittman_fast/[a-j]/<uuid>.pdf .
      The file s3://ahn-uploads/bittman/fast/index.json has the labels, titles, and filenames 
    for each recipe (chicken, fish, salads,...).
    Example:
      {name} --run

--
''' 
    if printmsg:
        print(msg)
        exit(1)
    else:
        return msg

def main():
    if len(sys.argv) == 1: usage(True)
    parser = argparse.ArgumentParser(usage=usage())
    parser.add_argument( "--run", required=True, action='store_true')
    args = parser.parse_args()
    run(args)
    
def run(args):
    pikedoc = pikepdf.Pdf.open(MASTER_PDF)
    with pdfplumber.open(MASTER_PDF) as pdf:
        pagenum = 0
        section = ''
        pagetext = ''
        start_page = 0
        recipe_flag = False
        oldsection = ''
        for pnum,page in enumerate(pdf.pages):
            #if pnum == 88:
            #    BP()
            #    tt=42
            pagetext = page.extract_text()
            lines = pagetext.split('\n')
            oldsection = section
            section = ' '.join( lines[-1].split()[1:])
            if 'SPEED' in lines[0] and 'SERVES' in lines[0]: # A recipe start page
                if recipe_flag: # A two page recipe
                    save_recipe( 'save', title=title, labels=[oldsection], pdf=recipe_pdf)
                start_page = pnum
                # Titles are bluish
                title_filter.state = 0
                title = page.filter(title_filter).extract_text()
                title = ' '.join(title.split())
                recipe_flag = True
                recipe_pdf = pikepdf.Pdf.new()
                recipe_pdf.pages.append( pikedoc.pages[pnum])
            elif recipe_flag: # Figure out whether we are still in the recipe
                if (
                        pnum - start_page > 1 # No recipe exceeds two pages
                        or page_starts_with_non_blue_caps( page) # Second page never starts with all black caps
                        or section != oldsection # Second page must be in same section
                ):
                    # A one page recipe
                    save_recipe( 'save', title=title, labels=[oldsection], pdf=recipe_pdf)
                    recipe_flag = False
                else:
                    recipe_pdf.pages.append( pikedoc.pages[pnum])

        save_recipe( 'done')
      
# (0.1882, 0.5804, 0.8392) bright blue
# (0.0549, 0.1725, 0.251) black / dark

def page_starts_with_non_blue_caps( page):
    n = 0
    for x in page.objects['char']:
        # invisible
        if not x['stroking_color']: continue
        n += 1
        if n > 3: return True
        # blue or lowercase
        if x['stroking_color'][2] > 0.5 or not x['text'].isupper():
            return False

def title_filter(x):
    ''' Find the first blue sequence of characters '''
    def bluish(x):
        if not x.get('stroking_color',''): return False
        if x.get('object_type','') != 'char': return False
        return x['stroking_color'][2] > 0.8

    if title_filter.state == 0:
        if  bluish(x): 
            title_filter.state = 1
            return True
    elif title_filter.state == 1:
        if  bluish(x): 
            return True
        else:
            title_filter.state = 2
            return False
    else:
        return False
title_filter.state = 0

def save_recipe( action, title='', labels=[], pdf=''):
    if action == 'init':
        save_recipe.index = []
        save_recipe.count = 0
    elif action == 'save':
        save_recipe.count += 1
        print( f' {save_recipe.count} {labels[0]} {title}')
        tempfname = 'temp.pdf'
        pdf.save(tempfname)
        with open(tempfname,'rb') as inf:
            fname = str(uuid.uuid4()) + '.pdf'
            subfolder = 'abcdefghij'[random.randint(0,9)]
            s3_write_to_file( inf, fname, subfolder)
        for label in labels:
            index_entry = { 'title':title, 'fname':f'{subfolder}/{fname}', 'label':label }
            save_recipe.index.append(index_entry)
    elif action == 'done':
        fname = 'index.json'
        s3_write_to_file( json.dumps( save_recipe.index, indent=4), fname)
save_recipe.index = []
save_recipe.count = 0

def s3_write_to_file( data, fname, subfolder=''):
    """ Store data in a file in our S3 folder """
    key = f'{S3_FOLDER}/{fname}'
    if subfolder: key = f'{S3_FOLDER}/{subfolder}/{fname}'
    S3.put_object( Body=data, Bucket=S3_BUCKET, Key=key)

if __name__ == '__main__':
  main()
