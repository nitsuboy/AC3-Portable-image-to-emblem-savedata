from PIL import Image, ImagePalette
from io import BytesIO
import PySimpleGUI as sg
import os, sys

debug = True
local = os.getcwd()

if debug:
    img = [Image.open("images/128x128.png")]
    back = {"AC3" : "images/backAC3.png",
            "ACLR" : "images/backACLR.png",
            "ACFF" : "images/backACFF.png"}
else:
    img = [Image.open(os.path.join(sys._MEIPASS, "128x128.png"))]
    back = {"AC3" : "backAC3.png",
            "ACLR" : "backACLR.png",
            "ACFF" : "backACFF.png"}

def convert_to_bytes(img):
   with BytesIO() as bio:
      img.save(bio, format="PNG")
      del img
      return bio.getvalue()

def open_emblem_from_savedata(filename):
    
    file = open(filename,'rb')
    file.seek(0, 2)
    file.seek(0 if file.tell() < 18432 else 32)
    emblem = file.read(16384)
    pal = file.read(1024)

    data = Image.frombytes('P',(128,128), emblem)
    data.putpalette(pal,rawmode="RGBA")
    pal = ImagePalette.ImagePalette("RGBA",pal)
    
    return [data,pal]

def open_emblem_from_image(filename):
    data = Image.open(filename).convert('P')
    data = data.resize((128,128))
    pal = ImagePalette.ImagePalette("RGBA",data.getpalette(rawmode='RGBA'))
    return [data,pal]

def write_save_logo(game):
    backpath = back[game] if debug else os.path.join(sys._MEIPASS, back[game]) 
    backim = Image.open(backpath)
    emblem = img[0].resize((78,78)).convert('RGBA')
    backim.paste(emblem,(1,1),emblem)
    backim.save("out/"+ game +"/ICON0.PNG",'PNG')

def write_emblem_to_savedata_AC3():
    newFile = open("out/AC3/SAVEDATA.BIN", "wb")
    newFile.write(b'\x05\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    newFile.write(img[0].tobytes())
    newFile.write(img[1].tobytes())

    while True:
        newFile.seek(0, 2)
        if newFile.tell() >= 18432:
            break
        newFile.write(b'\x00')
    
    write_save_logo("AC3")

def write_emblem_to_savedata_ACLR():
    newFile = open("out/ACLR/SAVEDATA.BIN", "wb")
    newFile.write(b'\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    newFile.write(img[0].tobytes())
    newFile.write(img[1].tobytes())

    while True:
        newFile.seek(0, 2)
        if newFile.tell() >= 18432:
            break
        newFile.write(b'\x00')

    write_save_logo("ACLR")

def write_emblem_to_savedata_ACFF():
    newFile = open("out/ACFF/DATA.BIN", "wb")
    newFile.write(img[0].tobytes())
    newFile.write(img[1].tobytes())

    while True:
        newFile.seek(0, 2)
        if newFile.tell() >= 17432:
            break
        newFile.write(b'\x00')
    
    write_save_logo("ACFF")
    
def write_emblem_to_image():
    img[0].save("out/emblem.png",'PNG')

sg.theme('DarkBrown4')

layout = [  [sg.Text("File",key="-PATH-")],
            [sg.Image(convert_to_bytes(img[0]), expand_x=True, expand_y=True , key='-IMAGE-')],
            [sg.Button(button_text="Open File"),
             sg.Button('Save to image')],
            [sg.Button('Save to AC3'),
             sg.Button('Save to ACFF'),
             sg.Button('Save to ACLR')]]

if debug:
    window = sg.Window('AC image to emblem data' ,layout ,size=(350,250) ,icon= "images/crest.ico")
else:
    window = sg.Window('AC image to emblem data',
                   layout ,size=(350,250),
                   icon=os.path.join(sys._MEIPASS, "crest.ico"))

if not os.path.exists('out'):
    os.makedirs('out')

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    elif event == 'Open File':
        window.disable()

        file = sg.popup_get_file('',
                                 multiple_files=False,
                                 no_window=True,
                                 file_types= [("Images", ("*.png","*.jpg")),("AC3P Savedata","*.BIN")],
                                 initial_folder=local)

        if file:
            window['-PATH-'].update(file)
        else:
            window['-PATH-'].update('')

        if file.endswith(tuple([".png",".jpg"])):
            img = open_emblem_from_image(file)
            window['-IMAGE-'].update(convert_to_bytes(img[0]))
        elif file.endswith('.BIN'):
            img = open_emblem_from_savedata(file)
            window['-IMAGE-'].update(convert_to_bytes(img[0]))
        
        window.enable()
        window.force_focus()

    elif event == 'Save to image':
        try:
            write_emblem_to_image()
        except Exception as e:
            sg.popup(f"Error : {str(e)}",title="Error")

    elif event == 'Save to AC3':
        try:
            if not os.path.exists('out/AC3'):
                os.makedirs('out/AC3')
            write_emblem_to_savedata_AC3()
        except Exception as e:
            sg.popup(f"Error : {str(e)}",title="Error")
    
    elif event == 'Save to ACFF':
        try:
            if not os.path.exists('out/ACFF'):
                os.makedirs('out/ACFF')
            write_emblem_to_savedata_ACFF()
        except Exception as e:
            sg.popup(f"Error : {str(e)}",title="Error")
    
    elif event == 'Save to ACLR':
        try:
            if not os.path.exists('out/ACLR'):
                os.makedirs('out/ACLR')
            write_emblem_to_savedata_ACLR()
        except Exception as e:
            sg.popup(f"Error : {str(e)}",title="Error")
        
window.close()