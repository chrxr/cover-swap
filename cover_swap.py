#!/usr/bin/python3

import os, shutil, zipfile, re, sys, errno

def main():
    begin_path = 'files/'
    end_path = 'files/copy/'
    extract_path = 'files/extracted/'
    repub_path = 'files/repubbed/'
    zip_list = [] 
    new_file_locs = {}
    file_list = get_file_list(begin_path)
    print('Got file list\n')
    for infile in file_list:
        file_locs = {} 
        copy_file(infile, begin_path, end_path)
        print('Copied EPUB\n')
        infile = ext_changer(end_path, infile)
        print('Changed to Zip\n')
        zip_check(end_path, zip_list, infile)
        print('Checked we only have Zips\n')
        extract_list = zip_opener(end_path, infile, extract_path, file_locs)
        print('Opened Zip\n')
        processing(end_path, extract_path, extract_list, file_locs)
        print('Finished processing\n')
        re_zip(repub_path, extract_path, extract_list,file_locs)
        print('All done\n')
        clean_up(end_path, extract_path)


    
#LISTS INPUT FILES
    
def get_file_list(begin_path):
    file_list = []
    listing = os.listdir(begin_path)
    try:
        for infile in listing:
            this_file = infile
            current_ext = os.path.splitext(this_file)[1]
            if current_ext == '.epub':
                file_list.append(infile)
    except:
        print("ERROR: You have no EPUB files in the files folder. Place one and only one EPUB in the files folder, then place the replacement cover in the new_cover folder.")
        sys.exit()
    if len(file_list) > 1:
        print("ERROR: You have more than one EPUB in the files folder. This script will only process one file at a time.")
        sys.exit()
    return file_list

#BACKUPS UP INPUT FILES, WORKS ON COPIES

def copy_file(infile, begin_path, end_path):
        src = begin_path + infile
        dst = end_path
        shutil.copy2(src, dst)

        # Will have to revisit this as it overwrites files. Need to add exception

#CHANGES EPUB EXTENSIONS TO ZIP, AND VICE VERSA
def ext_changer(end_path, infile):
    base = os.path.splitext(infile)[0]
    current_ext = os.path.splitext(infile)[1]
    if current_ext == '.epub':
        file_path = end_path + infile
        new_file = end_path + base + '.zip'
        os.rename(file_path, new_file)
    elif current_ext == '.zip':
        file_path = end_path + infile
        new_file = end_path + base + '.epub'
        os.rename(file_path, new_file)
    return new_file

#CHECKS FOR ZIP FILES AND SAVES THEM TO LIST

def zip_check(end_path, zip_list, infile):
        current_ext = os.path.splitext(infile)[1]
        if current_ext == '.zip':
            zip_list.append(infile)
            
#OPENS ZIP FILES, CREATES DIR, CREATES DICT OF FILE LOCATIONS, AND EXTRACTS FILES TO FOLDER

def zip_opener(end_path, infile, extract_path, file_locs):
        extract_list = {}
        zipper = zipfile.ZipFile(infile, 'r')
        file_name = os.path.split(infile)[1]
        minus_ext = os.path.splitext(file_name)[0]
        file_locs[minus_ext] = zipper.namelist()
        new_path = extract_path + minus_ext
        mkdir_p(new_path)
        zipper.extractall(path = new_path)
        extract_list[minus_ext] = new_path
        return extract_list
          
## REZIPS FILE AND CONVERTS TO EPUB

def re_zip(repub_path, extract_path, extract_list,file_locs):
    searcher = re.compile('mimetype')
    for key in extract_list:
        extracted_path = extract_path + key + '/'
        zip_path = repub_path + key + '.zip'
        zipper = zipfile.ZipFile(zip_path, 'a')
        for index, value in file_locs.items():
            if key == index:
                for ind_file_name in value:
                    if re.search(searcher, ind_file_name):
                        zipper.write(extracted_path + ind_file_name, ind_file_name)
                        for ind_file_name in value:
                            if re.search(searcher, ind_file_name):
                                continue
                            else:    
                                zipper.write(extracted_path + ind_file_name, ind_file_name)
                    else:
                        continue
            else:
                continue
        zipper.close()
    listing = os.listdir(repub_path)
    for infile in listing:
        base = os.path.splitext(infile)[0]
        current_ext = os.path.splitext(infile)[1]
        if current_ext == '.zip':
            file_path = repub_path + infile
            new_file = repub_path + base + '.epub'
            os.rename(file_path, new_file)
        else:
            continue
        
#ALL THE MAIN STUFF HAPPENS HERE       
        
def processing(end_path, extract_path, extract_list, file_locs):
    replacement_file = 'new_cover/cover.jpg'
    cover_locs = []
    for key in extract_list:
        for index, value in file_locs.items():
            if key == index:
                ind_ext_path = extract_list[key] + '/'
                for ind_file_name in value:
                    if re.search('/cover.jpg', ind_file_name):
                        cover_locs.append(ind_file_name)
                        ind_file_root = os.path.split(ind_file_name)[0]
                        file_to_be_replaced = ind_ext_path + ind_file_name
                        location = ind_ext_path + ind_file_root
                        overwrite_files(replacement_file, file_to_be_replaced, location)
    if len(cover_locs) < 1:
        print("ERROR: No file called cover.jpg was found in this EPUB file. Cover has not been replaced")
        clean_up(end_path, extract_path)
        sys.exit()
    elif len(cover_locs) > 1:
        print("ERROR: There is more than one file called cover.jpg in this EPUB file. Cover has not been replaced.")
        clean_up(end_path, extract_path)
        sys.exit()
     
######## MISC STUFF ############

#FILE OVERWRITER
def overwrite_files(file_name, ind_ext_path, location):
    try:
        os.remove(ind_ext_path)
        src = file_name
        dst = location
        shutil.copy2(src, dst) 
    except:
        print("ERROR: Either you do not have a cover.jpg file in the new_cover folder, or the file is named incorrectly.")
        sys.exit()
    
#REMOVE FILES IN DIR
def remove_files_in_dir(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
       
#DIRECTORY MAKER
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise
        
def clean_up(end_path, extract_path):
    remove_files_in_dir(end_path)
    remove_files_in_dir(extract_path)
        
        
if __name__ == "__main__": main()