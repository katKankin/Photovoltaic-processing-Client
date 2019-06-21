
# TECNOLÓGICO DE COSTA RICA
# CAMPUS TECNOLÓGICO LOCAL SEDE SAN CARLOS
# UNIDAD DE COMPUTACIÓN
# PRINCIPIOS DE SISTEMAS OPERATIVOS
# 2019
# -----------------------------------
# ESTUDIANTES:
# - CHRISTIAN SÁNCHEZ SALAS
# - KATHERINE TUZ CARRILLO
# -----------------------------------------------------------
import os
import time
from multiprocessing import Process
import glob
from socket import *
from threading import Thread
import queue
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from skimage.measure import compare_ssim as ssim
from skimage import img_as_float
from skimage.transform import resize
import sys
import cv2
import numpy as np
FLAG = True


def login_drive_api():
    """ function for login, -Try doing this automatically- """
    global gauth, drive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    # g_auth.Authorize() ?¡?¡?
    drive = GoogleDrive(gauth)
    # return drive


def start_client(ip_address):

    host = ip_address
    port = 12345
    ret_flag = "DONE"
    try:

        s = socket(AF_INET, SOCK_STREAM)
        s.connect((host, port))
    except error:
        print("SERVER IS OFF WORK NOW!")  # IN CASE SERVER ASIGNNED
        return ret_flag

    # message received from server
    data = s.recv(1024)

    # PROCESS IMGS

    print('Received from the server :', str(data.decode('ascii')))
    # close the connection

    ret_flag = str(data.decode('ascii'))
    if ret_flag != "DONE":
        download_folder(ret_flag)
        print("DISCARD PROCESS INITIATED...")
        discard_task(ret_flag)
        print(f'DISCARD PROCESS FINISHED\nDIRECTORY {ret_flag} UPDATED IN REPOSITORY')

    s.close()
    return ret_flag


def panel_recognition(image): #png format

    # READ THE MAIN IMAGE
    img = cv2.imread(image)

    #  CONVERT TO GRAY.
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # RAD THE SAMPLE
    template = cv2.imread('sample5.png', 0)

    #  STORE WIDTH AND HEIGTH 
    w, h = template.shape[::-1]

    # MATCH TEMPLATE
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

    
    threshold = 0.1

    # STORE THE MATCH COOR
    loc = np.where(res >= threshold)

    # DRAWING A YELLOW SQUARE
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 1)
    return img

def get_images(img_list, folder_name):
    i = 1
    for file1 in img_list:
        print('Downloading {} from GDrive ({}/{})'.format(file1['title'], i, len(img_list)))
        # CHANGE THE DIRECTION:
        file1.GetContentFile(r'C:\Users\Kathe\Desktop\testImager\\'+folder_name+"\\" + file1['title'])
        i += 1


def download_folder(folder_name):
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    folder_id = "NO"
   
    try:
        
        print("CREATING FOLDER\n")
        # CHANGE THE DIRECTION:
        new_folder = r'C:\Users\Kathe\Desktop\testImager\\'+folder_name
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
    except OSError:
        print('Error: directory of data already created! Gonna try another one!')

    for file1 in file_list:

        if file1['title'] == folder_name:

            folder_id = file1['id']
            break

    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(folder_id)}).GetList()
    get_images(file_list, folder_name)

    print("DOWNLOAD FINISHED!")


def create_folder(folder_name):
    folder_name = 'CHECKED_' + folder_name
    new_folder = drive.CreateFile({'title': '{}'.format(folder_name),
                                   'mimeType': 'application/vnd.google-apps.folder'})
    new_folder.Upload()
    return new_folder


def upload_img_to_folder(fname, folder):

    nfile = drive.CreateFile({'title': os.path.basename(fname),
                          'parents': [{u'id': folder['id']}]})
    nfile.SetContentFile(fname)
    nfile.Upload()


def compare_img(path_img_a, path_img_b):

    img_a = cv2.imread(path_img_a)
    img_b = cv2.imread(path_img_b)
    img_a = resize(img_a, (1024, 1024), anti_aliasing=True, preserve_range=True)
    img_b = resize(img_b, (1024, 1024), anti_aliasing=True, preserve_range=True)
    return ssim(img_a, img_b, multichannel=True)


def discard_task(to_process):
    # delete from drive
    new_folder = create_folder(to_process)
    imgs_list = os.listdir(to_process)
 
    for i in range(len(imgs_list)):
        j = i + 1
        if j == len(imgs_list):
            break
        elif j == len(imgs_list)-1:

            path_img_a = to_process+'/'+imgs_list[i]
            path_img_b = to_process+'/'+imgs_list[j]
            print(path_img_a)
            print(path_img_b)
            if(compare_img(path_img_a, path_img_b)) <= 0.1:
                img_a = panel_recognition(path_img_a) # this should be .png
                img_b = panel_recognition(path_img_b)

                cv2.imwrite(os.path.basename(path_img_a), img_a)
                # upload_img_to_folder(os.path.basename(path_img_a), new_folder)
                cv2.imwrite(os.path.basename(path_img_b), img_b)
               # upload_img_to_folder(os.path.basename(path_img_b), new_folder)

                # upload_img_to_folder(path_img_a, new_folder)
                # upload_img_to_folder(path_img_b, new_folder)
            else:

                cv2.imwrite(os.path.basename(path_img_b), img_b)
                upload_img_to_folder(os.path.basename(path_img_b), new_folder)
                # upload_img_to_folder(path_img_b, new_folder)
        else:
            path_img_a = to_process + '/' + imgs_list[i]
            path_img_b = to_process + '/' + imgs_list[j]
            img_a = panel_recognition(path_img_a)
            print(path_img_a)
            print(path_img_b)
            if (compare_img(path_img_a, path_img_b)) <= 0.1:

                cv2.imwrite(os.path.basename(path_img_a), img_a)
                # upload_img_to_folder(os.path.basename(path_img_a), new_folder)
                # upload_img_to_folder(path_img_a, new_folder)
            else:
                continue


if __name__ == '__main__':

     global IP
     IP = sys.argv[1]
    
    login_drive_api()
 
     while True:
    
         flag = start_client(IP)
         # c = input()
         if flag == "DONE":
             break
            # SE AGREGA EL TIME.SLEEP PARA PRUEBAS CON POCOS VIDEOS
         time.sleep(10) 
   
    print(0)

