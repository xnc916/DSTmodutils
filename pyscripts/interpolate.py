import json
import sys
import matplotlib.bezier as bz
import copy
_print=print
def print(*args):
    if 1:
        _print(*args)
def interpolate_bezier(c1, c2, c3, c4, t):
    fn = bz.BezierSegment([[0, 0], [c1, c2], [c3, c4], [1, 1]])
    return fn.point_at_t(t)[1]


def interpolate_linear(v1, v2, t,isangle=False):
    v1=v1 or 0
    v2=v2 or 0
    # print(v1,v2,t,isangle)
    # Handle angles near 0 and 360 degrees
    if isangle:
        if abs(v1-v2)>180:
            if v1<v2:
                v1=v1+360
            else:
                v2=v2+360
        return v1 + (v2 - v1) * t % 360
    else:
        return v1 + (v2 - v1) * t


def processscon(filepath):
    data = None
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if data:
        processroot(data)
    return data


def processroot(r, framerate=30):
    for i in r['entity']:
        for j in i['animation']:
            processanim(j, framerate)
            j['interval'] = int(1000 / framerate)
           # j['length']=


def processanim(a, framerate=30):
    timelines = a['timeline']
    a['timeline'] = []
    for id, i in enumerate(timelines):
        intp = interpolate(i['key'], framerate)
        newtl = {
            'id': id,
            'key': intp,
            'name': i['name'],
            'obj': i['obj'],
        }
        a['timeline'].append(newtl)
    mainline = a['mainline']
    newmainline=processmainline(mainline,a['timeline'])
    #transpose layer and timeline, and insert
    #key 0 cannot be deleted
    mainline['key']=[mainline['key'][0]]
    idx=0
    for i,layer in enumerate(newmainline):
        for j,keyframe in enumerate(layer):
            #print(j,keyframe['time'])
            if j>0:
                if len(mainline['key'])<=j:
                        mainline['key'].append({
                                    "bone_ref": [],
                                    "id": idx+1,
                                    "object_ref": [],
                                    "time":keyframe['time']
                                    })
                        idx+=1
                mainline['key'][j]['object_ref'].insert(0,keyframe)
    return a
def extractmainline(m):
    key=m['key']
    data=[]
    for i in key:
        o=i['object_ref']
        data.append(copy.copy(o))
    #transpose timeline and layer
    ret=[[]for i in range(len(data[0]))]
    for i,v in enumerate(data):
        for k,d in enumerate(v):
            ret[int(d['timeline'])].append(d)
    return ret
def processmainline(m,t):
    mdata=extractmainline(m)
    newmainline=[[]for i in range(len(t[0]['key']))]
    for layer in t:
        layerid=layer['id']
        for frame in layer['key']:
            if frame==0:
                continue
            framedata=newmainline[layerid]
            time=frame['time']
            keyid=frame['keyid']
            obj=frame['object']
            print(layerid,keyid,time)
            keyinfo=mdata[layerid][keyid]
            newinfo={}
            newinfo['id']=keyinfo['id']
            newinfo['key']=frame['id']
            newinfo['timeline']=keyinfo['timeline']
            newinfo['z_index']=keyinfo['z_index']
            newinfo['time']=time
            framedata.append(newinfo)
    return newmainline

def interpolate(data, framerate=30):
    frames = []
    framerate = 1000 / framerate
    frame_rate = 1 / framerate
    if 'time' not in data[0]:
        data[0]['time'] = 0
    for frame in range(0, int(data[-1]['time'] * frame_rate + 1)):

        # Find keyframes between which this frame falls
        keyframe1 = None
        keyframe2 = None
        for keyframe in data:
            if frame >= frame_rate * keyframe['time']:
                keyframe1 = keyframe
            else:
                if not keyframe2:
                    keyframe2 = keyframe
                    break

        if not keyframe1 or not keyframe2:
            print("Invalid keyframe: frame=", frame, "t=", frame * framerate,"kf:",keyframe1, keyframe2)
            raise ValueError("Invalid keyframe")
            continue
        t = (frame - frame_rate * keyframe1['time']) / \
            (keyframe2['time'] - keyframe1['time']) * framerate
       # print(    f'frame {frame:02d}:time {frame*framerate:.0f}<{keyframe1["time"]}-{keyframe2["time"]}')
        #assert (frame == 0 and t < 1e-5) or (frame != 0 and t >1e-5), f'{frame},{t}'
        if t==0:
            #straigit append
            dat=copy.copy(keyframe1)
            dat['keyid']=keyframe1['id']
            frames.append(dat)
            continue
        object = {}

        if keyframe1.get('curve_type') == 'bezier':
            c1 = keyframe1.get('c1')
            c2 = keyframe1.get('c2')
            c3 = keyframe1.get('c3')
            c4 = keyframe1.get('c4')

            object['x'] = interpolate_linear(keyframe1['object']['x'],
                                             keyframe2['object']['x'],
                                             interpolate_bezier(c1, c2, c3, c4, t))

            object['y'] = interpolate_linear(keyframe1['object']['y'],
                                             keyframe2['object']['y'],
                                             interpolate_bezier(c1, c2, c3, c4, t))

            object['angle'] = interpolate_linear(keyframe1['object'].get('angle'),
                                                 keyframe2['object'].get('angle'),
                                                 interpolate_bezier(c1, c2, c3, c4, t),isangle=1)

            object['scale_x'] = interpolate_linear(keyframe1['object']['scale_x'],
                                                   keyframe2['object']['scale_x'],
                                                   interpolate_bezier(c1, c2, c3, c4, t))

            object['scale_y'] = interpolate_linear(keyframe1['object']['scale_y'],
                                                   keyframe2['object']['scale_y'],
                                                   interpolate_bezier(c1, c2, c3, c4, t))
        else:
            object['x'] = interpolate_linear(keyframe1['object']['x'],
                                             keyframe2['object']['x'],
                                             t)
            object['y'] = interpolate_linear(keyframe1['object']['y'],
                                             keyframe2['object']['y'],
                                             t)
            object['angle'] = interpolate_linear(keyframe1['object'].get('angle'),
                                                 keyframe2['object'].get('angle'),
                                                 t,isangle=1)
            object['scale_x'] = interpolate_linear(keyframe1['object']['scale_x'],
                                                   keyframe2['object']['scale_x'],
                                                   t)
            object['scale_y'] = interpolate_linear(keyframe1['object']['scale_y'],
                                                   keyframe2['object']['scale_y'],
                                                   t)
        # Copy other properties from previous keyframe
        object['file'] = keyframe1['object']['file']
        object['folder'] = keyframe1['object']['folder']

        dat = {
            'time': round(frame * framerate),
            'object': object,
            'keyid':keyframe1['id']
        }
        try:
            dat['spin'] = keyframe1['spin']
        except BaseException:
            pass

        frames.append(dat)

    # Reassign ids and times
    for i, frame in enumerate(frames):
        frame['id'] = i

    return frames


def savedata(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python interpolate.py input.scon [output_interp.scon]")
        sys.exit(0)
    args = sys.argv[1:]
    inputfile = args[0]
    outputfile = args[1] if len(args) > 1 else inputfile.replace(".", "_interp.")
    data = processscon(inputfile)
    savedata(outputfile, data)


if '__main__' == __name__:
    main()
