import os.path
from tkinter import messagebox, ttk, filedialog as fd
from tkinter import *
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk, ImageOps
from imagemanip import image_manipulation
from extracttext import return_text

root = TkinterDnD.Tk()
root.title("OCRProject v2")
root.geometry("300x200")
root.resizable(False, False)
ico = PhotoImage(file='ocrp.png')
root.iconphoto(False, ico)
can = Canvas(root, height=200, width=300, bg='white')
can.pack()
dnd_img = PhotoImage(file='dnd.png')
can.create_image(0, 0, image=dnd_img, anchor=NW)
radius = 10
index = 0
c = Canvas(root, width=0, height=0)
b_can = Canvas(root, width=0, height=0)
draw_poly = True


def text_isolation(file_path):
    global c, b_can, root
    c.destroy()
    b_can.destroy()
    can.destroy()
    bg_img = Image.open(file_path)
    aspect_r = bg_img.width / bg_img.height
    scale_r = bg_img.height / 800
    bg_img = bg_img.resize(size=(int(aspect_r * 800), 800), resample=2)
    w = bg_img.width
    h = bg_img.height
    size_str = str(w) + "x" + str(h + 55)
    reset_img = bg_img.copy()
    threshold_img = None
    bg_img = ImageTk.PhotoImage(bg_img)
    root.geometry(size_str)
    sl_val1 = DoubleVar()
    sl_val1.set(85.0)
    sl_val2 = DoubleVar()
    sl_val2.set(170.0)

    co_ords = [[int(0.2 * w), int(0.2 * h)],
               [int(0.8 * w), int(0.2 * h)],
               [int(0.8 * w), int(0.8 * h)],
               [int(0.2 * w), int(0.8 * h)]]

    c = Canvas(root, width=w, height=h, bg='black')
    c.pack()

    def trigger_ocr():
        global c, b_can
        text = return_text(threshold_img)
        b_can.destroy()
        c.destroy()
        root.geometry("500x400")
        text_box = Text(root, width=50, height=25, font=('Calibri', 14))
        text_box.pack()
        text_box.insert('end', text)

    def trigger_sliders():
        global draw_poly, c, root, b_can
        nonlocal bg_img, reset_img
        sent_coords = [[co_ords[0][0], co_ords[0][1]],
                       [co_ords[1][0], co_ords[1][1]],
                       [co_ords[2][0], co_ords[2][1]],
                       [co_ords[3][0], co_ords[3][1]]]
        isolated_img = image_manipulation(co_ords=sent_coords, file_path=file_path, scale_r=scale_r)
        draw_poly = False
        n_aspect = isolated_img.width / isolated_img.height
        if n_aspect >= 1:
            nw, nh = 1000, int(1000 * (1 / n_aspect))
        else:
            nw, nh = int(n_aspect * 1000), 1000

        n_size_str = str(nw) + "x" + str(nh + 105)
        root.geometry(n_size_str)
        bg_img = isolated_img.resize(size=(nw, nh), resample=2)
        bg_img = ImageOps.grayscale(bg_img)
        reset_img = bg_img.copy()
        bg_img = ImageTk.PhotoImage(bg_img)
        c.destroy()
        b_can.destroy()
        c = Canvas(root, width=nw, height=nh, bg='black')
        c.pack()
        b_can = Canvas(root, width=nw, height=105, bg='white')
        scale_prompt = ttk.Label(b_can, text='Adjust the sliders to best isolate the text.')
        scale_prompt.pack()
        scale1 = ttk.Scale(b_can,
                           orient='horizontal',
                           from_=0,
                           to=255,
                           command=moved_slider,
                           variable=sl_val1,
                           length=nw - 10)
        scale1.pack()
        scale2 = ttk.Scale(b_can,
                           orient='horizontal',
                           from_=0,
                           to=255,
                           command=moved_slider,
                           variable=sl_val2,
                           length=nw - 10)
        scale2.pack()
        ttk.Button(b_can, text="Confirm", command=trigger_ocr).pack()
        b_can.pack()
        draw_screen()
        # text = return_text(isolated_img)
        # print(text)

    b_can = Canvas(root, width=w, height=35, bg='white')
    ttk.Label(b_can, text='Highlight the area of the image where you want to scan for text (please keep perspective '
                          'in mind).').pack()
    ttk.Button(b_can, text="Confirm", command=trigger_sliders).pack()
    b_can.pack()

    def moved_slider(slider_val):
        nonlocal bg_img
        nonlocal reset_img, sl_val1, sl_val2, threshold_img
        threshold_img = reset_img.copy()
        threshold_img = threshold_img.point(lambda x: 255 if sl_val1.get() < x < sl_val2.get() else 0)
        bg_img = ImageTk.PhotoImage(threshold_img)
        draw_screen()

    def d_circle(r, x, y):
        return c.create_oval(x - r, y - r, x + r, y + r, outline='lightgrey', fill='white')

    def draw_screen():
        nonlocal bg_img
        c.create_image(0, 0, image=bg_img, anchor=NW)
        if draw_poly:
            c.create_polygon(co_ords, fill='#80b332', width=2, stipple='gray50', outline='white')
            for i in range(4):
                d_circle(radius, co_ords[i][0], co_ords[i][1])

    def mover(x, y, i):
        if x >= w:
            co_ords[i][0] = w
        elif x <= 0:
            co_ords[i][0] = 0
        else:
            co_ords[i][0] = x

        if y >= h:
            co_ords[i][1] = h
        elif y <= 0:
            co_ords[i][1] = 0
        else:
            co_ords[i][1] = y

        # print(co_ords)
        c.delete('all')

    def update_coordinates(e):
        global index
        if co_ords[0][0] - radius * 2 <= e.x <= co_ords[0][0] + radius * 2 and \
                co_ords[0][1] - radius * 2 <= e.y <= co_ords[0][1] + radius * 2:
            index = 0

        elif co_ords[1][0] - radius * 2 <= e.x <= co_ords[1][0] + radius * 2 and \
                co_ords[1][1] - radius * 2 <= e.y <= co_ords[1][1] + radius * 2:
            index = 1

        elif co_ords[2][0] - radius * 2 <= e.x <= co_ords[2][0] + radius * 2 and \
                co_ords[2][1] - radius * 2 <= e.y <= co_ords[2][1] + radius * 2:
            index = 2

        elif co_ords[3][0] - radius * 2 <= e.x <= co_ords[3][0] + radius * 2 and \
                co_ords[3][1] - radius * 2 <= e.y <= co_ords[3][1] + radius * 2:
            index = 3

        mover(e.x, e.y, index)
        draw_screen()

    draw_screen()
    c.bind('<B1-Motion>', update_coordinates)
    root.mainloop()
    exit(1)


def drop(event):
    if event.data[0] == '{':
        event.data = event.data[1:-1]
    if event.data[-4:] == '.png' or event.data[-4:] == '.jpg':
        text_isolation(event.data)
    else:
        messagebox.showerror(title='Error', message='Invalid file format!')


can.drop_target_register(DND_FILES)
can.dnd_bind('<<Drop>>', drop)


def open_image():
    filetypes = (
        ('Image files', '*.jpg *.png'),
    )
    file = fd.askopenfile(filetypes=filetypes)
    try:
        file_path = os.path.abspath(file.name)
    except AttributeError:
        messagebox.showerror(title='Error', message='No file selected!')
    else:
        text_isolation(file_path)
        exit(1)


def about():
    msg_text = 'Optical Character Recognition Project \n\nmade by \n-Samir Amin'
    messagebox.showinfo(title='About', message=msg_text)


def usage():
    msg_text = "\n1. Open the image from which you'd like to scan the text.\n\n2. Highlight the text by moving the " \
               "corners of the rectangle, and press the confirm button\n\n3. Adjust the sliders so as to best isolate" \
               "the text.\n\n4. Press the confirm button once again; the application will then output the scanned " \
               "text into a text-box. "

    messagebox.showinfo(title='Usage', message=msg_text)


menu_bar = Menu(root)

m_file = Menu(menu_bar, tearoff=0)
m_file.add_command(label='Open', command=open_image)
m_file.add_separator()
m_file.add_command(label='Exit', command=root.quit)

menu_bar.add_cascade(label='File', menu=m_file)

m_help = Menu(menu_bar, tearoff=0)
m_help.add_command(label="About", command=about)
m_help.add_separator()
m_help.add_command(label="Usage", command=usage)
menu_bar.add_cascade(label="Help", menu=m_help)

root.config(menu=menu_bar)
root.mainloop()
exit(2)
