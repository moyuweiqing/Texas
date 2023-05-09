from PIL import Image, ImageFont, ImageDraw

cardnum = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
flowers = {'spade': '♠', 'heart': '♥', 'diamond': '♦', 'club': '♣'}
for c in cardnum:
    for f in flowers.keys():
        im = Image.new('RGB', (100, 150), (255, 255, 255))
        dr = ImageDraw.Draw(im)
        ft = ImageFont.truetype(font='arial', size=40, encoding='gb18030')
        if f == 'heart' or f == 'diamond':
            dr.text((30, 50), c + flowers[f], fill='#FF0000', font=ft)
        else:
            dr.text((30, 50), c + flowers[f], fill='#000000', font=ft)
        im.save('./cards/' + c + f + '.jpg')

im = Image.new('RGB', (100, 150), (255, 255, 255)).save('./cards/block.gif')