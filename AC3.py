from PIL import Image, ImagePalette
from io import BytesIO
import PySimpleGUI as sg
import os, sys

local = os.getcwd()

#os.path.join(os.environ["_MEIPASS2"], "images/128x128.png")

#img = [Image.open("images/128x128.png")]
img = [Image.open(os.path.join(sys._MEIPASS, "128x128.png"))]

def convert_to_bytes(img):
   with BytesIO() as bio:
      img.save(bio, format="PNG")
      del img
      return bio.getvalue()

def open_emblem_from_savedata(filename):
    file = open(filename,'rb')
    file.seek(32)
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

def write_emblem_to_savedata():
    newFile = open("out/SAVEDATA.BIN", "wb")
    newFile.write(b'\x05\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    newFile.write(img[0].tobytes())
    newFile.write(img[1].tobytes())

    while True:
        newFile.seek(0, 2)
        if newFile.tell() >= 18432:
            break
        newFile.write(b'\x00')

def write_emblem_to_image():
    img[0].save("out/emblem.png",'PNG')

def write_save_logo():
    #back = Image.open("images/back.png")
    back = Image.open(os.path.join(sys._MEIPASS, "back.png"))
    emblem = img[0].resize((78,78)).convert('RGBA')
    back.paste(emblem,(1,1),emblem)
    back.save("out/ICON0.PNG",'PNG')

sg.theme('DarkBrown4')

layout = [  [sg.Text("File",key="-PATH-")],
            [sg.Image(convert_to_bytes(img[0]), expand_x=True, expand_y=True , key='-IMAGE-')],
            [sg.Button(button_text="Open File"),
             sg.Button('Save image'),
             sg.Button('Save SAVEDATA')] ]

#window = sg.Window('AC3 image to emblem savedata',
#                   layout ,size=(350,250),
#                   icon= "images/crest.ico")
window = sg.Window('AC3 image to emblem savedata',
                   layout ,size=(350,250),
                   icon=os.path.join(sys._MEIPASS, "crest.ico"))

if not os.path.exists('out'):
    os.makedirs('out')

while True:
    event, values = window.read()
    print(event)

    if event == sg.WIN_CLOSED:
        print("cu")
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

    elif event == 'Save image':
        try:
            write_emblem_to_image()
        except Exception as e:
            sg.popup(f"Error : {str(e)}",title="Error")

    elif event == 'Save SAVEDATA':
        try:
            write_emblem_to_savedata()
            write_save_logo()
        except Exception as e:
            sg.popup(f"Error : {str(e)}",title="Error")
        
window.close()