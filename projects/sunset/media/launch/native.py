"""Native projection helpers retained exactly for the accepted SUNSET film."""
from functools import lru_cache
import hashlib
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[4]
BUNDLE = ROOT / '.publication/sunset-final'
FONT = BUNDLE / 'assets/Geist.ttf'
W,H,FPS,FRAMES = 1920,1080,30,1340
DURATION = FRAMES/FPS
INK,WHITE,DARK,MINT,CORAL,QUIET = '#183c2e','#f3efdc','#071a17','#baf4c6','#f47b50','#88aca0'
EVENTS = {'target':341,'match':500,'release':525,'credit':549,'claim':609,'confirmed':644,'paid':654}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


@lru_cache(maxsize=32)
def font(size, weight=500):
    result = ImageFont.truetype(str(FONT), size)
    result.set_variation_by_axes([weight])
    return result


def text(image, xy, words, size, colour=INK, weight=500, anchor=None):
    ImageDraw.Draw(image).text(xy, words, font=font(size, weight), fill=colour, anchor=anchor)


def smooth(value):
    x = max(0, min(1, value))
    return x*x*(3-2*x)


def project_corners(center,size,camera,ry=0,rz=0):
    w,h=size; cx,cy,push=camera
    ay,az=math.radians(ry),math.radians(rz)
    result=[]
    for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]:
        x,z=u*math.cos(ay),-u*math.sin(ay)
        px=center[0]+x*math.cos(az)-v*math.sin(az)
        py=center[1]+x*math.sin(az)+v*math.cos(az)
        depth=1600+center[2]+z-push
        assert depth>150, 'Paper crossed the camera near plane'
        result.append((960+1600*(px-cx)/depth,540+1600*(py-cy)/depth))
    return result


def project_sheet(frame,texture,center,size,camera,ry=0,rz=0):
    quad=project_corners(center,size,camera,ry,rz)
    left=max(0,math.floor(min(p[0] for p in quad))); right=min(W,math.ceil(max(p[0] for p in quad)))
    top=max(0,math.floor(min(p[1] for p in quad))); bottom=min(H,math.ceil(max(p[1] for p in quad)))
    if right<=left or bottom<=top: return
    # Inverse homography maps the actual projected plane to its original pixels.
    rows=[]; values=[]
    for (x,y),(u,v) in zip(quad,[(0,0),(texture.width,0),(texture.width,texture.height),(0,texture.height)]):
        x-=left; y-=top
        rows.extend([[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]])
        values.extend([u,v])
    coefficients=np.linalg.solve(np.asarray(rows),np.asarray(values))
    warped=texture.transform((right-left,bottom-top),Image.Transform.PERSPECTIVE,
                             coefficients,Image.Resampling.BICUBIC)
    frame.paste(warped,(left,top),warped)


def ramp(value,a,b):
    return smooth((value-a)/(b-a))


def lerp(a,b,p):
    return tuple(x+(y-x)*p for x,y in zip(a,b))


def rotate(x,y,z,camera):
    angle=math.radians(camera[3] if len(camera)>3 else 0)
    dx=x-1330
    return 1330+dx*math.cos(angle)+z*math.sin(angle),y,-dx*math.sin(angle)+z*math.cos(angle)


def sheet(frame,texture,center,size,camera,ry=0,rz=0):
    yaw=camera[3] if len(camera)>3 else 0
    return project_sheet(frame,texture,rotate(*center,camera),size,camera[:3],ry=ry+yaw,rz=rz)


def point(x,y,z,camera):
    x,y,z=rotate(x,y,z,camera)
    cx,cy,push=camera[:3];depth=1600+z-push
    assert depth>200
    return (960+1600*(x-cx)/depth,540+1600*(y-cy)/depth)


def line(frame,points,colour,width=2):
    ImageDraw.Draw(frame).line(points,fill=colour,width=width,joint='curve')


@lru_cache(maxsize=1)
def backdrop():
    y,x=np.mgrid[0:H,0:W]
    glow=np.exp(-(((x-1330)/850)**2+((y-620)/650)**2)*1.4)
    rim=np.exp(-(((x-1750)/650)**2+((y-180)/500)**2)*1.8)
    pixels=np.zeros((H,W,3),np.float32)+np.array([5,18,17])
    pixels+=glow[:,:,None]*np.array([9,29,21])+rim[:,:,None]*np.array([12,11,3])
    return Image.fromarray(np.uint8(np.clip(pixels,0,255)))


def stage(time,camera=(960,540,0),floor=True):
    frame=backdrop().copy();d=ImageDraw.Draw(frame)
    if floor:
        drift=65*math.sin(time*.14)
        for x in range(350,2600,150):
            a,b=point(x+drift,960,-100,camera),point(x+drift,960,1800,camera)
            d.line([a,b],fill='#153b31',width=1)
        for z in range(-100,1900,160):
            d.line([point(250+drift,960,z,camera),point(2600+drift,960,z,camera)],fill='#153b31',width=1)
    return frame


def glow(frame,paths,colour=MINT,width=3):
    # Low-resolution bloom keeps the local renderer fast and lettering sharp.
    light=Image.new('RGB',(480,270));d=ImageDraw.Draw(light)
    for path in paths:d.line([(x/4,y/4) for x,y in path],fill=colour,width=max(1,round(width/2)),joint='curve')
    light=light.filter(ImageFilter.GaussianBlur(3)).resize((W,H),Image.Resampling.BILINEAR)
    a=np.asarray(frame,dtype=np.uint16)+np.asarray(light,dtype=np.uint16)//2
    frame.paste(Image.fromarray(np.uint8(np.minimum(a,255))))
    for path in paths:line(frame,path,colour,width)


def orbit(frame,camera,time,radius=500,alpha=1,complete=False):
    points=[]
    for angle in np.linspace(0,math.tau,121):
        points.append(point(1330+radius*math.cos(angle),820,180+radius*.65*math.sin(angle),camera))
    line(frame,points,'#315e4d',2)
    if alpha:
        offset=time*.12
        segment=[point(1330+radius*math.cos(a),820,180+radius*.65*math.sin(a),camera) for a in np.linspace(offset,offset+(math.tau if complete else 1.1),90)]
        glow(frame,[segment],MINT if complete else '#92c8aa',3)


def block(frame,center,size,camera,colour=MINT):
    x,y,z=center;s=size/2
    coordinates=[(x+a*s,y+b*s,z+c*s) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    p=[point(*q,camera) for q in coordinates];d=ImageDraw.Draw(frame)
    for face,fill in [([1,5,6,2],'#28614b'),([0,4,5,1],'#7eaa86'),([0,1,2,3],colour)]:
        poly=[p[i] for i in face];d.polygon(poly,fill=fill);d.line(poly+[poly[0]],fill='#d5f3d3',width=2)


def platform(frame,camera,width=590,y=895):
    top=[point(1330+width*.5*math.cos(a),y,100+width*.32*math.sin(a),camera) for a in np.linspace(0,math.tau,7)[:-1]]
    bottom=[(x,b+48) for x,b in top];d=ImageDraw.Draw(frame)
    d.polygon(bottom,fill='#0a201c')
    for i in range(6):
        j=(i+1)%6;d.polygon([top[i],top[j],bottom[j],bottom[i]],fill='#143a30' if i%2 else '#1c493b')
    d.polygon(top,fill='#224a3c');glow(frame,[top+[top[0]]],MINT,2)


def label(frame,words,colour=QUIET):
    ImageDraw.Draw(frame).rectangle((0,985,W,H),fill=DARK)
    text(frame,(108,1005),words,34,colour)


def state(n):
    if n<EVENTS['credit']:return 'sealed' if n<EVENTS['release'] else 'public'
    if n<EVENTS['claim']:return 'Ready to claim'
    if n<EVENTS['confirmed']:return 'Claiming…'
    if n<EVENTS['paid']:return 'Confirmed'
    return 'Paid'
